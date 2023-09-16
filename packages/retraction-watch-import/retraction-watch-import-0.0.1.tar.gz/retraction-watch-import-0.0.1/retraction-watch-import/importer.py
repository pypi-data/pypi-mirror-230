import io
import json
import os
from datetime import datetime
from datetime import timedelta

import requests
from clannotation.annotator import Annotator as Annotator
from claws import aws_utils
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

API_BASE = "https://api.crossref.org"

USER_AGENT = (
    f"retraction_watch_importer:{os.path.basename(__file__)} "
    f"; (mailto:labs@crossref.org)"
)

HEADERS = {"User-Agent": USER_AGENT}

BUCKET = "outputs.research.crossref.org"
PREFIX = "api_artifacts"


class RetractionWatch:
    def import_retraction_watch_data(self, instrumentation) -> None:
        """
        The main import logic
        :return: None
        """

        aws_connector = aws_utils.AWSConnector(
            bucket="outputs.research.crossref.org", unsigned=False
        )

        csv = self._get_retraction_watch(aws_connector)

        if csv is None:
            print("Error loading Retraction Watch data")
            return

        print(f"Loaded Retraction Watch data")

        with io.StringIO(csv) as f:
            import csv

            reader = csv.DictReader(f)
            row: dict

            for row in reader:
                self._process_retraction_row(
                    aws_connector=aws_connector,
                    row=row,
                    instrumentation=instrumentation,
                )

    def _process_retraction_row(
        self,
        aws_connector,
        row: dict,
        commit: bool = True,
        instrumentation=None,
    ) -> None:
        """
        Process a row from the CSV
        :param aws_connector: an AWSConnector instance
        :param row: the row from the CSV
        :param commit: whether to commit the annotation to S3
        :param instrumentation: an instrumentation instance
        :return: None
        """

        # extract the DOI and its MD5
        doi, doi_md5 = self._extract_doi(row)

        # extract fields from the CSV
        (
            nature,
            notes,
            reasons,
            retraction_doi,
            urls,
            retraction_date,
            record_id,
        ) = self._extract_fields(row)

        # generate the "about" block
        about, about_url, warnings = self._generate_about_block()

        # create the final template
        template = self._generate_json(
            about=about,
            about_url=about_url,
            warnings=warnings,
            nature=nature,
            notes=notes,
            reasons=reasons,
            retraction_doi=retraction_doi,
            urls=urls,
            retraction_date=retraction_date,
            asserted_by="https://ror.org/005b4k264",
        )

        current_key = f"annotations/works/{doi_md5}/retractions.json"

        # delete this key
        try:
            aws_connector.s3_client.delete_object(
                Bucket="outputs.research.crossref.org", Key=current_key
            )
        except Exception as e:
            print(f"Couldn't delete: {e}")

        current_key = f"annotations/works/{doi_md5}/updates.json"

        # determine whether we should create, replace, or append the retraction
        # information. Default is to overwrite.
        template = self._update_doi_entry(
            aws_connector, current_key, doi, instrumentation, nature, template
        )

        template = self._flatten_template(doi, instrumentation, template)

        # write the annotation to S3
        if commit:
            self._write_annotation(
                aws_connector,
                current_key,
                template,
            )

    @staticmethod
    def _flatten_template(doi, instrumentation, template):
        """
        Flatten the template into a list
        :param doi: the DOI
        :param instrumentation: an instrumentation instance
        :param template: the template
        :return: the flattened template
        """
        if type(template) is not list:
            template = [template]

            if instrumentation is not None:
                instrumentation.logger.info(
                    f"Converting entry for {doi} to a list."
                )
        return template

    @staticmethod
    def _get_retraction_watch(aws_connector=None) -> str | None:
        """
        Download the retraction watch dump from S3
        :return: CSV string
        """
        current_date = datetime.now()

        if aws_connector is None:
            aws_connector = aws_utils.AWSConnector(
                bucket="org.crossref.research.retractionwatch", unsigned=False
            )

        # look back over the past 30 days
        for x in range(1, 30):
            try:
                s3_path = (
                    f"uploads/RWDBDNLD{current_date.strftime('%Y%m%d')}.csv"
                )

                print(f"Trying {s3_path}")

                csv = aws_connector.s3_client.get_object(
                    Bucket="org.crossref.research.retractionwatch",
                    Key=s3_path,
                )["Body"].read()

                csv_str = csv.decode("latin1")

                print(f"Loaded {s3_path}")
                return csv_str
            except Exception as e:
                # take one day off current date
                current_date = current_date - timedelta(days=1)
                print(f"Looking back in time... {e}")

        print("No data file found")

    @staticmethod
    def _update_doi_entry(
        aws_connector, current_key, doi, instrumentation, nature, template
    ):
        try:
            existing_entry = json.loads(
                aws_connector.s3_obj_to_str(
                    bucket="outputs.research.crossref.org",
                    s3_path=current_key,
                    raise_on_fail=True,
                )
            )

            tripped = False

            for entry in existing_entry:
                if entry["retraction-nature"] == nature:
                    # if we get here, we have found an entry with the same
                    # nature as the one we are trying to add. We should append
                    # to this, but we need to inline modify the template with
                    # new data
                    tripped = True

                    if instrumentation is not None:
                        instrumentation.logger.info(
                            f"Entry for {doi} is a duplicate. "
                            f"Overwriting section."
                        )

                    index_of_entry = existing_entry.index(entry)
                    existing_entry[index_of_entry] = template.copy()

                    template = existing_entry

            if not tripped:
                # we didn't find an entry with the same nature, so we should
                # append the new entry to the existing entry
                if type(template) is not list:
                    template = [template]

                template.extend(existing_entry)

                if instrumentation:
                    instrumentation.logger.info(
                        f"Entry for {doi} is not a duplicate. Appending."
                    )

        except Exception as e:
            print(f"ERROR loading existing DOI entry: {e}")

        return template

    @staticmethod
    def _write_annotation(aws_connector, destination, template) -> None:
        """
        Write the annotation to S3
        :param aws_connector: an AWSConnector instance
        :param destination: the destination path
        :param template: the JSON template
        :return: None
        """
        aws_connector.push_json_to_s3(
            json_obj=template,
            bucket="outputs.research.crossref.org",
            path=destination,
        )

    @staticmethod
    def _generate_json(
        about,
        about_url,
        warnings,
        nature,
        notes,
        reasons,
        retraction_doi,
        urls,
        retraction_date,
        asserted_by,
    ) -> dict:
        """
        Generate the JSON template
        :param about: the "about" text
        :param about_url: the "about" URL
        :param warnings: the stability warning
        :param nature: the nature of the retraction
        :param notes: notes about the retraction
        :param reasons: reasons for the retraction
        :param retraction_doi: the DOI of the retraction (not the original DOI)
        :param urls: URLs associated with the retraction
        :param retraction_date: the date of the retraction
        :param asserted_by: the entity asserting the retraction
        :return: the JSON template
        """
        template = {
            "about": {
                "source": about,
                "source_url": about_url,
                "stability": warnings,
            },
            "asserted-by": asserted_by,
            "target-doi": retraction_doi,
            "reasons": reasons,
            "update-nature": nature,
            "notes": notes,
            "urls": urls,
            "update-date": str(retraction_date),
            # date has to be pre-serialized
        }
        return template

    @staticmethod
    def _generate_about_block(
        asserted_by="Retraction Watch",
        about_url="https://retractionwatch.com",
    ) -> tuple[str, str, str]:
        """
        Generate the "about" block
        :return: the "about" block and "about" url
        """
        about = (
            "This work has an update record associated with it, "
            f"asserted by {asserted_by}."
        )
        warning = (
            "The keys used in this API block are unstable and subject to "
            "change at any future time."
        )

        return about, about_url, warning

    def _extract_fields(
        self,
        row,
    ) -> tuple[str, str, list[str], str, list[str], datetime, str]:
        """
        Extract the fields from the CSV row
        :param row: the CSV row
        :return: the fields extracted (nature, notes, reasons, retraction_doi,
         urls, date, record_id)
        """

        retraction_doi = (
            "https://doi.org/" + row["RetractionDOI"]
            if not row["RetractionDOI"].startswith("http")
            else row["RetractionDOI"]
        )
        reasons = [sub[1:] for sub in row["Reason"].split(";") if len(sub) > 0]
        nature = row["RetractionNature"]
        notes = row["Notes"]
        urls = row["URLS"].split(";")
        try:
            date = self._date_serial_number(int(row["RetractionDate"]))
        except ValueError:
            date = self._date_serial_number(row["RetractionDate"])

        record_id = row["Record ID"]

        return nature, notes, reasons, retraction_doi, urls, date, record_id

    @staticmethod
    def _extract_doi(row) -> tuple[str, str]:
        """
        Extract the DOI and its MD5 from the CSV row
        :param row: the CSV row
        :return: the DOI and its MD5
        """
        doi = row["OriginalPaperDOI"]
        doi_md5 = Annotator.doi_to_md5(doi)
        return doi, doi_md5

    @staticmethod
    def _date_serial_number(serial_number: int | str) -> datetime:
        """
        Convert an Excel serial number to a Python datetime object
        :param serial_number: the date serial number
        :return: a datetime object
        """
        if type(serial_number) is str:
            try:
                return datetime.strptime(serial_number, "%m/%d/%Y 0:00")
            except ValueError:
                return datetime.strptime(
                    "01/01/1900 0:00",
                    "%m/%d/%Y 0:00",
                )

        # Excel stores dates as "number of days since 1900"
        delta = datetime(
            1899,
            12,
            30,
        ) + timedelta(days=serial_number)
        return delta

    def _pull_crossmark(self, instrumentation):
        class APISummariesError(Exception):
            """Exception class from which every exception in this library will
            derive. It enables other projects using this library to catch
            all errors coming from the library with a single "except" statement
            """

            pass

        class TenaciousnessCrapiFailed(APISummariesError):
            """Tenaciousness was not enough"""

            pass

        @retry(
            stop=stop_after_attempt(5),
            wait=wait_random_exponential(multiplier=1, max=60),
        )
        def _crapi(spec):
            query = spec["query"]
            headers = spec["headers"]

            res = requests.get(query, headers=headers)

            if res.status_code == 200:
                return res.json()["message"]

            raise TenaciousnessCrapiFailed(
                f"An HTTP error occurred: status:{res.status_code}"
            )

        @retry(
            stop=stop_after_attempt(5),
            wait=wait_random_exponential(multiplier=1, max=60),
        )
        def _send_prepared_request(s, prepared):
            res = s.send(prepared, stream=True)

            if res.status_code != 200:
                raise TenaciousnessCrapiFailed(
                    f"An HTTP error occurred: status:{res.status_code}"
                )
            else:
                return res

        def _all_results_cursor(
            api=API_BASE,
            route_name="members",
            rows=10,
            headers=None,
            parameters: dict = None,
        ):
            query_params = {"cursor": "*", "rows": rows}

            if parameters:
                query_params = query_params | parameters

            result_template = {
                "status": "ok",
                "message-type": "member-list",
                "message-version": "1.0.0",
                "message": {
                    "items-per-page": 10,
                    "query": {"start-index": 0, "search-terms": "null"},
                    "next-cursor": "CR-LABS-FINAL",
                    "total-results": 24066,
                    "items": [],
                },
            }

            with requests.Session() as s:
                while True:
                    prepared = requests.Request(
                        method="GET",
                        url=f"{api}/{route_name}",
                        params=query_params,
                        headers=headers,
                    ).prepare()

                    res = _send_prepared_request(s, prepared)

                    record = res.json()

                    # are we done?
                    if not record["message"]["items"]:
                        result_template["message"]["total-results"] = record[
                            "message"
                        ]["total-results"]

                        result_template["message"]["items-per-page"] = record[
                            "message"
                        ]["total-results"]

                        result_template["message-type"] = record["message-type"]
                        result_template["message-version"] = record[
                            "message-version"
                        ]
                        result_template["status"] = record["status"]

                        return (
                            record["message"]["total-results"],
                            result_template,
                        )

                    # more to go
                    result_template["message"]["items"] += record["message"][
                        "items"
                    ]

                    query_params["cursor"] = record["message"]["next-cursor"]

        cursor_routes = ["works"]

        from claws import aws_utils

        aws_connector = aws_utils.AWSConnector(
            bucket="outputs.research.crossref.org", unsigned=False
        )

        for route in cursor_routes:
            instrumentation.logger.info(f"Fetching data for {route}")
            params = {"filter": "is-update:true,update-type:retraction"}
            _, all_data = _all_results_cursor(
                route_name=route, rows=1000, headers=HEADERS, parameters=params
            )

            for item in all_data["message"]["items"]:
                self._process_item(aws_connector, instrumentation, item)

            instrumentation.logger.info(f"Saved data for {route}")

        pass

    def _process_item(self, aws_connector, instrumentation, item):
        (
            doi,
            doi_md5,
            nature,
            record_id,
            retraction_date,
            template,
        ) = self._generate_template(item)

        # delete any old retracted value
        current_key = f"annotations/works/{doi_md5}/retractions.json"

        # delete this key
        try:
            aws_connector.s3_client.delete_object(
                Bucket="outputs.research.crossref.org", Key=current_key
            )
        except Exception as e:
            print(f"Couldn't delete: {e}")

        current_key = f"annotations/works/{doi_md5}/updates.json"
        # determine whether we should create, replace, or append the
        # retraction information. Default is to overwrite.
        template = self._update_doi_entry(
            aws_connector,
            current_key,
            doi,
            instrumentation,
            nature,
            template,
        )

        template = self._flatten_template(doi, instrumentation, template)

        # write the annotation to S3
        self._write_annotation(
            aws_connector,
            current_key,
            template,
        )

    def _generate_template(self, item):
        doi = item["DOI"]
        doi_md5 = Annotator.doi_to_md5(doi)
        retraction_doi = "https://doi.org/" + item["update-to"][0]["DOI"]
        retraction_date = item["update-to"][0]["updated"]["date-time"]
        record_id = doi_md5
        nature = "Crossmark Retraction"

        # generate the "about" block
        about, about_url, warnings = self._generate_about_block(
            asserted_by="Publisher via Crossmark",
            about_url="https://www.crossref.org/services/crossmark/",
        )
        # create the final template
        template = self._generate_json(
            about=about,
            about_url=about_url,
            warnings=warnings,
            nature=nature,
            notes=[],
            reasons=[],
            retraction_doi=retraction_doi,
            urls=[],
            retraction_date=retraction_date,
            asserted_by="Crossmark",
        )
        return doi, doi_md5, nature, record_id, retraction_date, template
