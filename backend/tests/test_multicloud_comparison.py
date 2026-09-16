import unittest

from app.agent.agent import CLOUD_FUNCTION_MAP, set_comparison_group
from app.agent.runner import _task_prompt
from app.domain.calculators.registry import get_calculator


class MulticloudComparisonPromptTest(unittest.TestCase):
    def test_agent_can_store_a_dynamic_comparison_group(self):
        context = type("Context", (), {"state": {}})()

        response = set_comparison_group(
            "Consulta analítica serverless",
            '["bigquery", "aws_athena", "azure_synapse_sql"]',
            "Todos cobram pelo processamento de consultas sem cluster dedicado.",
            "direct",
            context,
        )

        self.assertEqual(response["status"], "success")
        self.assertEqual(
            context.state["comparison_groups"][0]["service_ids"],
            ["bigquery", "aws_athena", "azure_synapse_sql"],
        )

    def test_dms_is_not_an_automatic_datastream_equivalent(self):
        prompt = _task_prompt(
            "context",
            "gcp",
            "multicloud",
            "Pipeline com CDC",
            [],
            True,
        )

        self.assertNotIn("Datastream = DMS", prompt)
        self.assertIn("não use azure_dms nem aws_dms", prompt)

    def test_warehouse_chooses_one_aws_query_engine(self):
        self.assertIn(
            "escolha aws_athena OU aws_redshift",
            CLOUD_FUNCTION_MAP,
        )

    def test_bi_uses_creator_seats_and_excludes_databricks_sql(self):
        self.assertIn(
            "aws_quicksight.authors com o mesmo total de usuários",
            CLOUD_FUNCTION_MAP,
        )
        self.assertIn("Não use dbx_sql como licença de BI", CLOUD_FUNCTION_MAP)


class AzureDmsNotesTest(unittest.TestCase):
    def test_result_mentions_the_183_day_free_period(self):
        calculator = get_calculator("azure_dms")
        result = calculator.calculate({"billable_hours": 0})

        self.assertTrue(any("183 dias" in note for note in result.notes))


if __name__ == "__main__":
    unittest.main()
