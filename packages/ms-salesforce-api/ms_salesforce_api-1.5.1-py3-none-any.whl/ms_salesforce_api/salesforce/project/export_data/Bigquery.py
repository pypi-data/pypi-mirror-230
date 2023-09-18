import logging
from itertools import islice
from urllib.parse import quote

from gc_google_services_api.bigquery import BigQueryManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class BigQueryExporter:
    """
    Initializes the Bigquery exporter with the given project ID and dataset ID.

    Args:
        project_id (str): The ID of the Google Cloud project.
        dataset_id (str): The ID of the BigQuery dataset.
    """

    def __init__(self, project_id, dataset_id):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = BigQueryManager(
            project_id=project_id, dataset_id=dataset_id
        )
        self.batch_size = 200
        self.schemas = {
            "opportunities": {
                "amount": "FLOAT",
                "controller_email": "STRING",
                "controller_sub_email": "STRING",
                "cost_center": "STRING",
                "created_at": "TIMESTAMP",
                "currency": "STRING",
                "invoicing_country_code": "STRING",
                "jira_task_url": "STRING",
                "last_updated_at": "TIMESTAMP",
                "lead_source": "STRING",
                "operation_coordinator_email": "STRING",
                "operation_coordinator_sub_email": "STRING",
                "opportunity_name": "STRING",
                "opportunity_percentage": "STRING",
                "profit_center": "STRING",
                "project_code": "STRING",
                "project_id": "STRING",
                "project_name": "STRING",
                "project_start_date": "DATE",
                "project_tier": "STRING",
                "stage": "STRING",
            },
            "billing_lines": {
                "billing_amount": "FLOAT",
                "billing_date": "DATE",
                "billing_period_ending_date": "DATE",
                "billing_period_starting_date": "DATE",
                "billing_plan_amount": "STRING",
                "billing_plan_billing_date": "DATE",
                "billing_plan_item": "STRING",
                "billing_plan_service_end_date": "DATE",
                "billing_plan_service_start_date": "DATE",
                "created_date": "TIMESTAMP",
                "currency": "STRING",
                "hourly_price": "FLOAT",
                "id": "STRING",
                "last_modified_date": "TIMESTAMP",
                "name": "STRING",
                "project_id": "STRING",
                "revenue_dedication": "FLOAT",
                "project_code": "STRING",
            },
            "project_line_items": {
                "country": "STRING",
                "created_date": "TIMESTAMP",
                "effort": "STRING",
                "ending_date": "DATE",
                "id": "STRING",
                "last_modified_date": "TIMESTAMP",
                "ms_pli_name": "STRING",
                "product_name": "STRING",
                "project_id": "STRING",
                "project_code": "STRING",
                "quantity": "FLOAT",
                "starting_date": "DATE",
                "total_price": "STRING",
                "unit_price": "STRING",
            },
            "accounts": {
                "assigment_group": "STRING",
                "billing_address": "STRING",
                "billing_city": "STRING",
                "billing_country": "STRING",
                "billing_postal_code": "STRING",
                "billing_state_code": "STRING",
                "billing_street": "STRING",
                "business_function": "STRING",
                "business_name": "STRING",
                "cif": "STRING",
                "company_invoicing": "STRING",
                "created_date": "STRING",
                "currency_code": "STRING",
                "fax": "STRING",
                "id": "STRING",
                "invoicing_email": "STRING",
                "mail_invoicing": "STRING",
                "name": "STRING",
                "office": "STRING",
                "payment_terms": "STRING",
                "pec_email": "STRING",
                "phone": "STRING",
                "project_id": "STRING",
                "project_code": "STRING",
                "sap_id": "STRING",
                "tax_category": "STRING",
                "tax_classification": "STRING",
                "tax_id_type": "STRING",
                "tier": "STRING",
                "website": "STRING",
                "account_customer_groupId": "STRING",
                "account_customer_subgroupId": "STRING",
            },
            "groups": {
                "project_id": "STRING",
                "project_code": "STRING",
                "groupid": "STRING",
                "name": "STRING",
                "start_date": "STRING",
                "end_date": "STRING",
                "bqid": "STRING",
                "pck_type": "STRING",
                "supervisor_email": "STRING",
                "owner_email": "STRING",
            },
            "subgroups": {
                "groupid": "STRING",
                "name": "STRING",
                "subgroupid": "STRING",
                "start_date": "STRING",
                "end_date": "STRING",
                "bqid": "STRING",
                "owner_email": "STRING",
            },
        }

        for table_name, table_schema in self.schemas.items():
            self.client.create_table_if_not_exists(table_name, table_schema)

    def _execute_query(self, query, log_id, default_error_value=None):
        custom_error_value = f"{log_id}_custom_error"

        result = self.client.execute_query(
            query,
            custom_error_value,
        )

        if result == custom_error_value:
            logging.error(
                f"[ERROR - _execute_query]: Error executing query for {log_id} in BigQuery."
            )
            result = default_error_value

        return result

    def _export_opportunities(self, opportunities):
        opportunities_values = []
        for opp in opportunities:
            project_start_date = (
                f'DATE "{opp["project_start_date"]}"'
                if opp["project_start_date"]
                else "NULL"
            )
            profit_center = (
                f'"{opp["profit_center"]}"' if opp["profit_center"] else "NULL"
            )
            cost_center = (
                f'"{opp["cost_center"]}"' if opp["cost_center"] else "NULL"
            )

            opportunities_values.append(
                f"""
                (
                    "{opp['currency']}",
                    {opp['amount']},
                    "{opp['invoicing_country_code']}",
                    "{opp['operation_coordinator_email']}",
                    "{opp['operation_coordinator_sub_email']}",
                    TIMESTAMP "{opp['created_at']}",
                    TIMESTAMP "{opp['last_updated_at']}",
                    "{opp['opportunity_name']}",
                    "{opp['stage']}",
                    "{opp['lead_source']}",
                    "{opp['project_code']}",
                    "{opp['project_id']}",
                    "{opp['project_name']}",
                    {project_start_date},
                    "{opp['controller_email']}",
                    "{opp['controller_sub_email']}",
                    {profit_center},
                    {cost_center},
                    "{opp['project_tier']}",
                    "{quote(opp['jira_task_url'], safe='s')}",
                   "{opp['opportunity_percentage']}"
                )
                """
            )
        if opportunities_values:
            insert_opportunities_query = f"""
                INSERT INTO `{self.project_id}.{self.dataset_id}.opportunities` (
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
                ) VALUES {', '.join(opportunities_values)};
            """

            insert_opportunities_query = (
                insert_opportunities_query.replace("\n", "")
                .replace("    ", "")
                .replace("  ", "")
            )

            self._execute_query(
                query=insert_opportunities_query, log_id="INSERT_opportunities"
            )

    def _export_billing_lines(self, opportunities):
        total_billing_lines = sum(
            len(opp["billing_lines"]) for opp in opportunities
        )

        for i in range(0, total_billing_lines, self.batch_size):
            batch_opportunities = []
            batch_billing_lines = []

            for opp in opportunities:
                remaining_lines = islice(
                    opp["billing_lines"], i, i + self.batch_size
                )
                batch_opportunities.append(opp)
                batch_billing_lines.extend(remaining_lines)

                if len(batch_billing_lines) >= self.batch_size:
                    self._process_billing_lines_batch(batch_billing_lines)

                    batch_opportunities = []
                    batch_billing_lines = []

            if batch_billing_lines:
                self._process_billing_lines_batch(batch_billing_lines)

    def _process_billing_lines_batch(self, billing_lines):
        billing_lines_values = []
        for bl in billing_lines:
            billing_date = (
                f'DATE "{bl["billing_date"]}"'
                if bl["billing_date"]
                else "NULL"
            )
            billing_period_ending_date = (
                f'DATE "{bl["billing_period_ending_date"]}"'
                if bl["billing_period_ending_date"]
                else "NULL"
            )
            billing_period_starting_date = (
                f'DATE "{bl["billing_period_starting_date"]}"'
                if bl["billing_period_starting_date"]
                else "NULL"
            )
            billing_plan_billing_date = (
                f'DATE "{bl["billing_plan_billing_date"]}"'
                if bl["billing_plan_billing_date"]
                else "NULL"
            )
            billing_plan_service_end_date = (
                f'DATE "{bl["billing_plan_service_end_date"]}"'
                if bl["billing_plan_service_end_date"]
                else "NULL"
            )
            billing_plan_service_start_date = (
                f'DATE "{bl["billing_plan_service_start_date"]}"'
                if bl["billing_plan_service_start_date"]
                else "NULL"
            )

            billing_lines_values.append(
                f"""
                (
                    "{bl['id']}",
                    "{bl['project_id']}",
                    "{bl['project_code']}",
                    "{bl['name']}",
                    "{bl['currency']}",
                    TIMESTAMP "{bl['created_date']}",
                    TIMESTAMP "{bl['last_modified_date']}",
                    {bl['billing_amount'] if bl['billing_amount'] else 0.0},
                    {billing_date},
                    {billing_period_ending_date},
                    {billing_period_starting_date},
                    {bl['hourly_price'] if bl['hourly_price'] else 'NULL'},
                    {bl['revenue_dedication'] if bl['revenue_dedication'] else 'NULL'},
                    "{bl['billing_plan_amount']}",
                    {billing_plan_billing_date},
                    "{bl['billing_plan_item']}",
                    {billing_plan_service_end_date},
                    {billing_plan_service_start_date}
                )
                """
            )

        if billing_lines_values:
            insert_billing_lines_query = f"""
                INSERT INTO `{self.project_id}.{self.dataset_id}.billing_lines` (
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
                ) VALUES {', '.join(billing_lines_values)};
            """
            insert_billing_lines_query = (
                insert_billing_lines_query.replace("\n", "")
                .replace("    ", "")
                .replace("  ", "")
            )

            self._execute_query(
                query=insert_billing_lines_query, log_id="INSERT_billing_lines"
            )

    def _export_PLIs(self, opportunities):
        total_plis = sum(
            len(opp["project_line_items"]) for opp in opportunities
        )

        for i in range(0, total_plis, self.batch_size):
            batch_opportunities = []
            batch_plis = []

            for opp in opportunities:
                remaining_plis = islice(
                    opp["project_line_items"], i, i + self.batch_size
                )
                batch_opportunities.append(opp)
                batch_plis.extend(remaining_plis)
                project_id = opp["project_id"]
                project_code = opp["project_code"]

                if len(batch_plis) >= self.batch_size:
                    self._process_plis_batch(
                        batch_plis, project_id, project_code
                    )

                    batch_opportunities = []
                    batch_plis = []

            if batch_plis:
                self._process_plis_batch(batch_plis, project_id, project_code)

    def _process_plis_batch(self, plis, project_id, project_code):
        plis_values = []
        for pli in plis:
            effort = f"{pli['effort']}" if pli["effort"] else "NULL"
            total_price = (
                f"{pli['total_price']}" if pli["total_price"] else "NULL"
            )

            unit_price = (
                f"{pli['unit_price']}" if pli["unit_price"] else "NULL"
            )

            ending_date = (
                f'DATE "{pli["ending_date"]}"'
                if pli["ending_date"]
                else "NULL"
            )

            starting_date = (
                f'DATE "{pli["starting_date"]}"'
                if pli["starting_date"]
                else "NULL"
            )

            plis_values.append(
                f"""
                (
                    "{pli['country']}",
                    TIMESTAMP "{pli['created_date']}",
                    "{effort}",
                    {ending_date},
                    "{pli['id']}",
                    TIMESTAMP "{pli['last_modified_date']}",
                    "{pli['ms_pli_name']}",
                    "{pli['product_name']}",
                    {pli['quantity'] if pli['quantity'] else 0.0},
                    {starting_date},
                    "{total_price}",
                    "{unit_price}",
                    "{project_id}",
                    "{project_code}"
                )
                """
            )

        if plis_values:
            insert_plis_query = f"""
                INSERT INTO `{self.project_id}.{self.dataset_id}.project_line_items` (
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
                ) VALUES {', '.join(plis_values)};
            """

            insert_plis_query = (
                insert_plis_query.replace("\n", "")
                .replace("    ", "")
                .replace("  ", "")
            )

            self._execute_query(
                query=insert_plis_query, log_id="INSERT_project_line_items"
            )

    def _export_accounts(self, opportunities):
        account_values = []
        for opp in opportunities:
            account_name = (
                f'"{opp["account_name"]}"' if opp["account_name"] else "NULL"
            )
            assigment_group = (
                f'"{opp["account_assigment_group"]}"'
                if opp["account_assigment_group"]
                else "NULL"
            )
            account_tax_category = (
                f'"{opp["account_tax_category"]}"'
                if opp["account_tax_category"]
                else "NULL"
            )
            account_tax_classification = (
                f'"{opp["account_tax_classification"]}"'
                if opp["account_tax_classification"]
                else "NULL"
            )
            account_sap_id = (
                f'"{opp["account_sap_id"]}"'
                if opp["account_sap_id"]
                else "NULL"
            )
            account_business_function = (
                f'"{opp["account_business_function"]}"'
                if opp["account_business_function"]
                else "NULL"
            )
            account_tax_id_type = (
                f'"{opp["account_tax_id_type"]}"'
                if opp["account_tax_id_type"]
                else "NULL"
            )
            account_currency_code = (
                f'"{opp["account_currency_code"]}"'
                if opp["account_currency_code"]
                else "NULL"
            )
            account_created_date = (
                f'"{opp["account_created_date"]}"'
                if opp["account_created_date"]
                else "NULL"
            )
            account_tier = (
                f'"{opp["account_tier"]}"' if opp["account_tier"] else "NULL"
            )
            account_pec_email = (
                f'"{opp["account_pec_email"]}"'
                if opp["account_pec_email"]
                else "NULL"
            )
            account_phone = (
                f'"{opp["account_phone"]}"' if opp["account_phone"] else "NULL"
            )
            account_fax = (
                f'"{opp["account_fax"]}"' if opp["account_fax"] else "NULL"
            )
            account_website = (
                f'"{opp["account_website"]}"'
                if opp["account_website"]
                else "NULL"
            )
            account_cif = (
                f'"{opp["account_cif"]}"' if opp["account_cif"] else "NULL"
            )
            account_billing_country = (
                f'"{opp["account_billing_country"]}"'
                if opp["account_billing_country"]
                else "NULL"
            )
            account_business_name = (
                f'"{opp["account_business_name"]}"'
                if opp["account_business_name"]
                else "NULL"
            )
            account_billing_address = (
                f'"{opp["account_billing_address"]}"'
                if opp["account_billing_address"]
                else "NULL"
            )
            account_billing_city = (
                f'"{opp["account_billing_city"]}"'
                if opp["account_billing_city"]
                else "NULL"
            )
            account_billing_postal_code = (
                f'"{opp["account_billing_postal_code"]}"'
                if opp["account_billing_postal_code"]
                else "NULL"
            )
            account_billing_street = (
                f'"{opp["account_billing_street"]}"'
                if opp["account_billing_street"]
                else "NULL"
            )
            account_company_invoicing = (
                f'"{opp["account_company_invoicing"]}"'
                if opp["account_company_invoicing"]
                else "NULL"
            )
            account_office = (
                f'"{opp["account_office"]}"'
                if opp["account_office"]
                else "NULL"
            )
            account_payment_terms = (
                f'"{opp["account_payment_terms"]}"'
                if opp["account_payment_terms"]
                else "NULL"
            )
            account_billing_state_code = (
                f'"{opp["account_billing_state_code"]}"'
                if opp["account_billing_state_code"]
                else "NULL"
            )
            account_mail_invoicing = (
                f'"{opp["account_mail_invoicing"]}"'
                if opp["account_mail_invoicing"]
                else "NULL"
            )
            account_invoicing_email = (
                f'"{opp["account_invoicing_email"]}"'
                if opp["account_invoicing_email"]
                else "NULL"
            )
            account_customer_groupId = (
                f'"{opp["account_customer_groupId"]}"'
                if opp["account_customer_groupId"] is not None
                else "NULL"
            )
            account_customer_subgroupId = (
                f'"{opp["account_customer_subgroupId"]}"'
                if opp["account_customer_subgroupId"]
                else "NULL"
            )

            account_values.append(
                f"""
                (
                    "{opp['project_id']}",
                    "{opp['project_code']}",
                    {account_name},
                    {assigment_group},
                    {account_tax_category},
                    {account_tax_classification},
                    {account_sap_id},
                    {account_business_function},
                    {account_tax_id_type},
                    {account_currency_code},
                    {account_created_date},
                    {account_tier},
                    {account_pec_email},
                    {account_phone},
                    {account_fax},
                    {account_website},
                    {account_cif},
                    {account_billing_country},
                    {account_business_name},
                    {account_billing_address},
                    {account_billing_city},
                    {account_billing_postal_code},
                    {account_billing_street},
                    {account_company_invoicing},
                    {account_office},
                    {account_payment_terms},
                    {account_billing_state_code},
                    {account_mail_invoicing},
                    {account_invoicing_email},
                    {account_customer_groupId},
                    {account_customer_subgroupId}
                )
                """
            )

        if account_values:
            insert_accounts_query = f"""
                INSERT INTO `{self.project_id}.{self.dataset_id}.accounts` (
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
                ) VALUES {', '.join(account_values)};
            """
            insert_accounts_query = (
                insert_accounts_query.replace("\n", "")
                .replace("    ", "")
                .replace("  ", "")
            )

            self._execute_query(
                query=insert_accounts_query, log_id="INSERT_accounts"
            )

    def _export_groups(self, opportunities):
        group_values = []
        for opp in opportunities:
            group_id = (
                f'"{opp["group_groupid"]}"' if opp["group_groupid"] else "NULL"
            )
            group_name = (
                f'"{opp["group_name"]}"' if opp["group_name"] else "NULL"
            )

            group_start = (
                f'"{opp["group_start_date"]}"'
                if opp["group_start_date"]
                else "NULL"
            )

            group_end = (
                f'"{opp["group_end_date"]}"'
                if opp["group_end_date"]
                else "NULL"
            )

            group_bqid = (
                f'"{opp["group_bqid"]}"' if opp["group_bqid"] else "NULL"
            )

            group_pck_type = (
                f'"{opp["group_pck_type"]}"'
                if opp["group_pck_type"]
                else "NULL"
            )

            group_supervisor_email = (
                f'"{opp["group_supervisor_email"]}"'
                if opp["group_supervisor_email"]
                else "NULL"
            )

            group_owner_email = (
                f'"{opp["group_owner_email"]}"'
                if opp["group_owner_email"]
                else "NULL"
            )

            group_values.append(
                f"""
                (
                    "{opp['project_id']}",
                    "{opp['project_code']}",
                    {group_id},
                    {group_name},
                    {group_start},
                    {group_end},
                    {group_bqid},
                    {group_pck_type},
                    {group_supervisor_email},
                    {group_owner_email}

                )
                """
            )

        if group_values:
            insert_group_query = f"""
                INSERT INTO `{self.project_id}.{self.dataset_id}.groups` (
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
                ) VALUES {', '.join(group_values)};
            """
            insert_group_query = (
                insert_group_query.replace("\n", "")
                .replace("    ", "")
                .replace("  ", "")
            )

            self._execute_query(
                query=insert_group_query,
                log_id="INSERT_accounts",
            )

    def _export_subgroups(self, opportunities):
        group_values = []
        for opp in opportunities:
            if not opp["group_groupid"]:
                continue
            group_id = (
                f'"{opp["group_groupid"]}"' if opp["group_groupid"] else "NULL"
            )
            subgroup_id = (
                f'"{opp["subgroup_subgroupid"]}"'
                if opp["subgroup_subgroupid"]
                else "NULL"
            )
            subgroup_name = (
                f'"{opp["subgroup_name"]}"' if opp["subgroup_name"] else "NULL"
            )

            subgroup_start = (
                f'"{opp["subgroup_start_date"]}"'
                if opp["subgroup_start_date"]
                else "NULL"
            )

            subgroup_end = (
                f'"{opp["subgroup_end_date"]}"'
                if opp["subgroup_end_date"]
                else "NULL"
            )

            subgroup_bqid = (
                f'"{opp["subgroup_bqid"]}"' if opp["subgroup_bqid"] else "NULL"
            )

            subgroup_owner_email = (
                f'"{opp["subgroup_owner_email"]}"'
                if opp["subgroup_owner_email"]
                else "NULL"
            )

            group_values.append(
                f"""
                (
                    {group_id},
                    {subgroup_id},
                    {subgroup_name},
                    {subgroup_start},
                    {subgroup_end},
                    {subgroup_bqid},
                    {subgroup_owner_email}
                )
                """
            )

        if group_values:
            insert_group_query = f"""
                INSERT INTO `{self.project_id}.{self.dataset_id}.subgroups` (
                    groupid,
                    subgroupid,
                    name,
                    start_date,
                    end_date,
                    bqid,
                    owner_email
                ) VALUES {', '.join(group_values)};
            """
            insert_group_query = (
                insert_group_query.replace("\n", "")
                .replace("    ", "")
                .replace("  ", "")
            )

            self._execute_query(
                query=insert_group_query,
                log_id="INSERT_accounts",
            )

    def export_data(self, opportunities):
        opportunities_batches = [
            opportunities[i : i + self.batch_size]  # noqa: E203
            for i in range(0, len(opportunities), self.batch_size)
        ]
        for batch in opportunities_batches:
            self._export_opportunities(batch)

            self._export_billing_lines(batch)

            self._export_PLIs(batch)

            self._export_accounts(batch)

            self._export_groups(batch)

            self._export_subgroups(batch)

    def delete_all_rows(self):
        table_names = self.schemas.keys()
        for table_name in table_names:
            delete_query_table = f"DELETE FROM `{self.project_id}.{self.dataset_id}.{table_name}` WHERE true"
            self._execute_query(
                query=delete_query_table,
                log_id=f"delete_table_{table_name}",
            )
