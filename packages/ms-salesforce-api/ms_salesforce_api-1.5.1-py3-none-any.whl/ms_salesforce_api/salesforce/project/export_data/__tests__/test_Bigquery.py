import re
import unittest
from unittest import mock


class BigQueryExporterTestCase(unittest.TestCase):
    def setUp(self):
        self.project_id = "your-project-id"
        self.dataset_id = "your-dataset-id"

        self.opportunities = [
            {
                "account_assigment_group": "03",
                "account_billing_address": "211 Main Street, Webster, Maine, 01570, United "  # noqa: E501
                "States",
                "account_billing_city": "Webster",
                "account_billing_country": "US",
                "account_billing_postal_code": "01570",
                "account_billing_state_code": "ME",
                "account_billing_street": "211 Main Street",
                "account_business_function": "BP03",
                "account_business_name": "THE COMMERCE INSURANCE COMPANY",
                "account_cif": "042495247",
                "account_company_invoicing": "",
                "account_created_date": "2020-03-18T15:32:15.000+0000",
                "account_currency_code": "EUR",
                "account_customer_groupId": "1",
                "account_customer_subgroupId": "5",
                "account_fax": None,
                "account_invoicing_email": "client1@test.com",
                "account_mail_invoicing": "client1@test.com",
                "account_name": "MAPFRE USA",
                "account_office": "Making Science LLC",
                "account_payment_terms": "T060",
                "account_pec_email": None,
                "account_phone": None,
                "account_sap_id": "10000319",
                "account_tax_category": None,
                "account_tax_classification": "0",
                "account_tax_id_type": "US01",
                "account_tier": "T1",
                "account_website": None,
                "amount": 0,
                "billing_lines": [
                    {
                        "billing_amount": 6708.0,
                        "billing_date": "2022-08-31",
                        "billing_period_ending_date": "2022-08-31",
                        "billing_period_starting_date": "2022-08-01",
                        "billing_plan_amount": "6708",
                        "billing_plan_billing_date": "2022-08-31",
                        "billing_plan_item": "1",
                        "billing_plan_service_end_date": "2022-08-31",
                        "billing_plan_service_start_date": "2022-08-01",
                        "created_date": "2022-08-09T14:56:23.000+0000",
                        "currency": "USD",
                        "hourly_price": 65.0,
                        "id": "a0sAX000000I8lgYAC",
                        "last_modified_date": "2022-10-16T18:56:34.000+0000",
                        "name": "BL-000175313",
                        "project_code": "USMSEX05508",
                        "project_id": "a00AX000002DVi1YAG",
                        "revenue_dedication": 103.2,
                    }
                ],
                "controller_email": "employee4@test.com",
                "controller_sub_email": "employee3@test.com",
                "cost_center": "",
                "created_at": "2022-08-01T08:53:12.000+0000",
                "currency": "EUR",
                "group_bqid": "1",
                "group_end_date": "2100-12-12",
                "group_groupid": "a0cAX000000TSWUYA4",
                "group_name": "MAPFRE",
                "group_owner_email": "employee1@test.com",
                "group_pck_type": "Key Account",
                "group_start_date": "2023-06-01",
                "group_supervisor_email": "employee2@test.com",
                "invoicing_country_code": "US",
                "jira_task_url": "<a "
                "href=https://makingscience.atlassian.net/browse/ESMSBD0001-7168 "  # noqa: E501
                "target=_blank>View Jira Task</a>",
                "last_updated_at": "2023-09-01T10:00:54.000+0000",
                "lead_source": "Crosselling/upselling",
                "operation_coordinator_email": "employee5@test.com",  # noqa: E501
                "operation_coordinator_sub_email": "employee5@test.com",  # noqa: E501
                "opportunity_name": "New Site Mapfre AAA",
                "opportunity_percentage": 100.0,
                "profit_center": "200018",
                "project_code": "USMSEX05508",
                "project_id": "a00AX000002DVi1YAG",
                "project_line_items": [
                    {
                        "country": None,
                        "created_date": "2022-08-02T15:44:34.000+0000",
                        "effort": "516",
                        "ending_date": "2022-12-31",
                        "id": "a0VAX000000EE0b2AG",
                        "last_modified_date": "2023-06-20T22:33:36.000+0000",
                        "ms_pli_name": "USA_UX/UI Design_USMSEX05508",
                        "product_name": "UXUI Project",
                        "quantity": 516.0,
                        "starting_date": "2022-08-01",
                        "total_price": 33540.0,
                        "unit_price": 65.0,
                    },
                    {
                        "country": None,
                        "created_date": "2022-08-09T14:54:59.000+0000",
                        "effort": "331",
                        "ending_date": "2022-12-31",
                        "id": "a0VAX000000ELU52AO",
                        "last_modified_date": "2023-06-20T22:33:36.000+0000",
                        "ms_pli_name": "ES_UX/UI Design_USMSEX05508",
                        "product_name": "UXUI Project",
                        "quantity": 331.0,
                        "starting_date": "2022-08-01",
                        "total_price": 21515.0,
                        "unit_price": 65.0,
                    },
                ],
                "project_name": "MapfreAAA",
                "project_start_date": "2022-08-01",
                "project_tier": "Unkown",
                "stage": "Closed Won",
                "subgroup_bqid": "5",
                "subgroup_end_date": "2100-12-12",
                "subgroup_groupid": "a0cAX000000TSWUYA4",
                "subgroup_name": "MAPFRE USA",
                "subgroup_owner_email": "employee1@test.com",
                "subgroup_start_date": "2023-06-01",
                "subgroup_subgroupid": "a19AX0000004simYAA",
            }
        ]

        self.mock_bigquery_manager = mock.patch(
            "gc_google_services_api.bigquery.BigQueryManager"
        ).start()
        from ..Bigquery import BigQueryExporter

        self.exporter = BigQueryExporter(self.project_id, self.dataset_id)

    def tearDown(self):
        self.mock_bigquery_manager.reset_mock()

    def test_export_opportunities(self):
        self.exporter._export_opportunities(self.opportunities)

        expected_query = """
        INSERT INTO `your-project-id.your-dataset-id.opportunities` (
            currency,
            amount,
            invoicing_country_code,
            operation_coordinator_email,
            operation_coordinator_sub_email,
            created_at,
            last_updated_at,
            opportunity_name,
            stage,
            lead_source,
            project_code,
            project_id,
            project_name,
            project_start_date,
            controller_email,
            controller_sub_email,
            profit_center,
            cost_center,
            project_tier,
            jira_task_url,
            opportunity_percentage
        )
        VALUES (
            "EUR"
            ,0,
            "US",
            "employee5@test.com",
            "employee5@test.com",
            TIMESTAMP "2022-08-01T08:53:12.000+0000",
            TIMESTAMP "2023-09-01T10:00:54.000+0000",
            "New Site Mapfre AAA",
            "Closed Won",
            "Crosselling/upselling",
            "USMSEX05508",
            "a00AX000002DVi1YAG",
            "MapfreAAA",
            DATE "2022-08-01",
            "employee4@test.com",
            "employee3@test.com",
            "200018",
            NULL,
            "Unkown",
            "%3Ca%20href%3Dhttps%3A%2F%2Fmakingscience.atlassian.net%2Fbrowse%2FESMSBD0001-7168%20target%3D_blank%3EView%20Jira%20Task%3C%2Fa%3E",
            "100.0"
        );
        """
        execute_query_calls = self.exporter.client.execute_query.call_args_list

        expected_query_stripped = re.sub(r"\s+", "", expected_query)

        self.assertEqual(
            expected_query_stripped,
            re.sub(r"\s+", "", str(execute_query_calls[1][0][0])),
        )

    def test_export_billing_lines(self):
        self.exporter._export_billing_lines(self.opportunities)

        expected_query = """
        INSERT INTO `your-project-id.your-dataset-id.billing_lines` (
            id,
            project_id,
            project_code,
            name,
            currency,
            created_date,
            last_modified_date,
            billing_amount,
            billing_date,
            billing_period_ending_date,
            billing_period_starting_date,
            hourly_price,
            revenue_dedication,
            billing_plan_amount,
            billing_plan_billing_date,
            billing_plan_item,
            billing_plan_service_end_date,
            billing_plan_service_start_date)
        VALUES (
            "a0sAX000000I8lgYAC",
            "a00AX000002DVi1YAG",
            "USMSEX05508",
            "BL-000175313",
            "USD",
            TIMESTAMP "2022-08-09T14:56:23.000+0000",
            TIMESTAMP "2022-10-16T18:56:34.000+0000",
            6708.0,
            DATE "2022-08-31",
            DATE "2022-08-31",
            DATE "2022-08-01",
            65.0,103.2,
            "6708",
            DATE "2022-08-31",
            "1",
            DATE "2022-08-31",
            DATE "2022-08-01"
        );
        """
        execute_query_calls = self.exporter.client.execute_query.call_args_list
        expected_query_stripped = re.sub(r"\s+", "", expected_query)
        execute_query_stripped = re.sub(
            r"\s+", "", str(execute_query_calls[0][0][0])
        )

        self.assertEqual(execute_query_stripped, expected_query_stripped)

    def test_export_PLIs(self):
        self.exporter._export_PLIs(self.opportunities)

        expected_query = """
        INSERT INTO `your-project-id.your-dataset-id.project_line_items` (
            country,
            created_date,
            effort,
            ending_date,
            id,
            last_modified_date,
            ms_pli_name,
            product_name,
            quantity,
            starting_date,
            total_price,
            unit_price,
            project_id,
            project_code
        )
        VALUES (
            "None",
            TIMESTAMP "2022-08-02T15:44:34.000+0000",
            "516",
            DATE "2022-12-31",
            "a0VAX000000EE0b2AG",
            TIMESTAMP "2023-06-20T22:33:36.000+0000",
            "USA_UX/UI Design_USMSEX05508",
            "UXUI Project",
            516.0,
            DATE "2022-08-01",
            "33540.0",
            "65.0",
            "a00AX000002DVi1YAG",
            "USMSEX05508"
        ),
        (
            "None",
            TIMESTAMP "2022-08-09T14:54:59.000+0000",
            "331",
            DATE "2022-12-31",
            "a0VAX000000ELU52AO",
            TIMESTAMP "2023-06-20T22:33:36.000+0000",
            "ES_UX/UI Design_USMSEX05508",
            "UXUI Project",
            331.0,
            DATE "2022-08-01",
            "21515.0",
            "65.0",
            "a00AX000002DVi1YAG",
            "USMSEX05508"
        );
        """

        execute_query_calls = self.exporter.client.execute_query.call_args_list
        expected_query_stripped = re.sub(r"\s+", "", expected_query)
        execute_query_stripped = re.sub(
            r"\s+", "", str(execute_query_calls[0][0][0])
        )
        self.assertEqual(execute_query_stripped, expected_query_stripped)

    @mock.patch(
        "ms_salesforce_api.salesforce.project.export_data.Bigquery.BigQueryManager"  # noqa: E501
    )
    def test_export_data(self, mock_bq_manager):
        mock_client = mock.Mock()
        mock_bq_manager.return_value = mock_client

        self.exporter.export_data(self.opportunities)

        expected_opportunities_query = """
            INSERT INTO `your-project-id.your-dataset-id.opportunities` (
                currency,
                amount,
                invoicing_country_code,
                operation_coordinator_email,
                operation_coordinator_sub_email,
                created_at,
                last_updated_at,
                opportunity_name,
                stage,
                lead_source,
                project_code,
                project_id,
                project_name,
                project_start_date,
                controller_email,
                controller_sub_email,
                profit_center,
                cost_center,
                project_tier,
                jira_task_url,
                opportunity_percentage
            ) VALUES (
                "EUR",
                0,
                "US",
                "employee5@test.com",
                "employee5@test.com",
                TIMESTAMP "2022-08-01T08:53:12.000+0000",
                TIMESTAMP "2023-09-01T10:00:54.000+0000",
                "New Site Mapfre AAA",
                "Closed Won","Crosselling/upselling",
                "USMSEX05508",
                "a00AX000002DVi1YAG",
                "MapfreAAA",
                DATE "2022-08-01",
                "employee4@test.com",
                "employee3@test.com",
                "200018",
                NULL,
                "Unkown",
                "%3Ca%20href%3Dhttps%3A%2F%2Fmakingscience.atlassian.net%2Fbrowse%2FESMSBD0001-7168%20target%3D_blank%3EView%20Jira%20Task%3C%2Fa%3E",
                "100.0"
            );
        """

        expected_billing_lines_query = """
            INSERT INTO `your-project-id.your-dataset-id.billing_lines` (
                id,
                project_id,
                project_code,
                name,
                currency,
                created_date,
                last_modified_date,
                billing_amount,
                billing_date,
                billing_period_ending_date,
                billing_period_starting_date,
                hourly_price,
                revenue_dedication,
                billing_plan_amount,
                billing_plan_billing_date,
                billing_plan_item,
                billing_plan_service_end_date,
                billing_plan_service_start_date
            ) VALUES (
                "a0sAX000000I8lgYAC",
                "a00AX000002DVi1YAG",
                "USMSEX05508",
                "BL-000175313",
                "USD",
                TIMESTAMP "2022-08-09T14:56:23.000+0000",
                TIMESTAMP "2022-10-16T18:56:34.000+0000",
                6708.0,
                DATE "2022-08-31",
                DATE "2022-08-31",
                DATE "2022-08-01",
                65.0,
                103.2,
                "6708",
                DATE "2022-08-31",
                "1",
                DATE "2022-08-31",
                DATE "2022-08-01"
            );
        """

        expected_PLIs_query = """
            INSERT INTO `your-project-id.your-dataset-id.project_line_items` (
                country,
                created_date,
                effort,
                ending_date,
                id,
                last_modified_date,
                ms_pli_name,
                product_name,
                quantity,
                starting_date,
                total_price,
                unit_price,
                project_id,
                project_code
            ) VALUES (
                "None",
                TIMESTAMP "2022-08-02T15:44:34.000+0000",
                "516",
                DATE "2022-12-31",
                "a0VAX000000EE0b2AG",
                TIMESTAMP "2023-06-20T22:33:36.000+0000",
                "USA_UX/UI Design_USMSEX05508",
                "UXUI Project",
                516.0,
                DATE "2022-08-01",
                "33540.0",
                "65.0",
                "a00AX000002DVi1YAG",
                "USMSEX05508"
            ), (
                "None",
                TIMESTAMP "2022-08-09T14:54:59.000+0000",
                "331",
                DATE "2022-12-31",
                "a0VAX000000ELU52AO",
                TIMESTAMP "2023-06-20T22:33:36.000+0000",
                "ES_UX/UI Design_USMSEX05508",
                "UXUI Project",
                331.0,
                DATE "2022-08-01","21515.0",
                "65.0",
                "a00AX000002DVi1YAG",
                "USMSEX05508"
            );
        """

        expected_accounts_query = """
            INSERT INTO `your-project-id.your-dataset-id.accounts` (
                project_id,
                project_code,
                name,
                assigment_group,
                tax_category,
                tax_classification,
                sap_id,
                business_function,
                tax_id_type,
                currency_code,
                created_date,
                tier,
                pec_email,
                phone,
                fax,
                website,
                cif,
                billing_country,
                business_name,
                billing_address,
                billing_city,
                billing_postal_code,
                billing_street,
                company_invoicing,
                office,
                payment_terms,
                billing_state_code,
                mail_invoicing,
                invoicing_email,
                account_customer_groupId,
                account_customer_subgroupId
            ) VALUES (
                "a00AX000002DVi1YAG",
                "USMSEX05508",
                "MAPFRE USA",
                "03",
                NULL,
                "0",
                "10000319",
                "BP03",
                "US01",
                "EUR",
                "2020-03-18T15:32:15.000+0000",
                "T1",
                NULL,
                NULL,
                NULL,
                NULL,
                "042495247",
                "US",
                "THE COMMERCE INSURANCE COMPANY",
                "211 Main Street, Webster, Maine, 01570, United States",
                "Webster",
                "01570",
                "211 Main Street",
                NULL,
                "Making Science LLC",
                "T060",
                "ME",
                "client1@test.com",
                "client1@test.com",
                "1",
                "5"
            );
        """

        expected_group_query = """
            INSERT INTO `your-project-id.your-dataset-id.groups` (
                project_id,
                project_code,
                groupid,
                name,
                start_date,
                end_date,
                bqid,
                pck_type,
                supervisor_email,
                owner_email
            ) VALUES (
                "a00AX000002DVi1YAG",
                "USMSEX05508",
                "a0cAX000000TSWUYA4",
                "MAPFRE",
                "2023-06-01",
                "2100-12-12",
                "1",
                "Key Account",
                "employee2@test.com",
                "employee1@test.com"
            );
        """

        expected_subgroup_query = """
           INSERT INTO `your-project-id.your-dataset-id.subgroups` (
            groupid,
            subgroupid,
            name,
            start_date,
            end_date,
            bqid,
            owner_email
        ) VALUES (
            "a0cAX000000TSWUYA4",
            "a19AX0000004simYAA",
            "MAPFRE USA",
            "2023-06-01",
            "2100-12-12",
            "5",
            "employee1@test.com"
        );
        """

        execute_query_calls = self.exporter.client.execute_query.call_args_list

        expected_opportunities_query_stripped = re.sub(
            r"\s+", "", expected_opportunities_query
        )

        execute_opportunities_query_stripped = re.sub(
            r"\s+", "", str(execute_query_calls[1][0][0])
        )

        expected_billinglines_query_stripped = re.sub(
            r"\s+", "", expected_billing_lines_query
        )

        execute_billinglines_query_stripped = re.sub(
            r"\s+", "", str(execute_query_calls[0][0][0])
        )

        expected_pli_query_stripped = re.sub(r"\s+", "", expected_PLIs_query)
        execute_pli_query_stripped = re.sub(
            r"\s+", "", str(execute_query_calls[3][0][0])
        )

        expected_accounts_query_stripped = re.sub(
            r"\s+", "", expected_accounts_query
        )

        execute_accounts_query_stripped = re.sub(
            r"\s+", "", str(execute_query_calls[4][0][0])
        )

        expected_groups_query_stripped = re.sub(
            r"\s+", "", expected_group_query
        )

        execute_groups_query_stripped = re.sub(
            r"\s+", "", str(execute_query_calls[5][0][0])
        )

        expected_subgroups_query_stripped = re.sub(
            r"\s+", "", expected_subgroup_query
        )

        execute_subgroups_query_stripped = re.sub(
            r"\s+", "", str(execute_query_calls[6][0][0])
        )

        self.assertEqual(
            execute_opportunities_query_stripped,
            expected_opportunities_query_stripped,
        )

        self.assertEqual(
            execute_billinglines_query_stripped,
            expected_billinglines_query_stripped,
        )

        self.assertEqual(
            execute_pli_query_stripped,
            expected_pli_query_stripped,
        )
        self.assertEqual(
            execute_accounts_query_stripped,
            expected_accounts_query_stripped,
        )

        self.assertEqual(
            execute_groups_query_stripped,
            expected_groups_query_stripped,
        )

        self.assertEqual(
            execute_subgroups_query_stripped,
            expected_subgroups_query_stripped,
        )
