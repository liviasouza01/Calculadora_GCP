from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldSchema, ServiceDefinition


class AwsS3Calculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_s3",
        name="Amazon S3",
        category="Armazenamento",
        provider="aws",
        description="Object storage Standard (us-east-1, primeiros 50 TB).",
        fields=[
            FieldSchema(id="storage_gb", label="Dados armazenados", type="number", unit="GB", default=1000, min=0),
            FieldSchema(
                id="put_thousands",
                label="PUT/COPY/POST/LIST",
                type="number",
                unit="milhares/mês",
                default=10,
                min=0,
            ),
            FieldSchema(
                id="get_thousands",
                label="GET/SELECT",
                type="number",
                unit="milhares/mês",
                default=50,
                min=0,
            ),
        ],
        pricing_references=[
            to_reference(p.AWS_S3_STANDARD),
            to_reference(p.AWS_S3_PUT),
            to_reference(p.AWS_S3_GET),
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [
            to_line_item(p.AWS_S3_STANDARD, self.get_number(inputs, "storage_gb")),
            to_line_item(p.AWS_S3_PUT, self.get_number(inputs, "put_thousands")),
            to_line_item(p.AWS_S3_GET, self.get_number(inputs, "get_thousands")),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Intelligent-Tiering, Glacier e egress não estão neste item."],
        )


class AwsAthenaCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_athena",
        name="Amazon Athena",
        category="Warehouse e consulta",
        provider="aws",
        description="SQL serverless sobre o S3 (TB varrido).",
        fields=[
            FieldSchema(id="scanned_tb", label="Dados varridos", type="number", unit="TB/mês", default=5, min=0),
        ],
        pricing_references=[to_reference(p.AWS_ATHENA_SCAN)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [to_line_item(p.AWS_ATHENA_SCAN, self.get_number(inputs, "scanned_tb"))]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Use Parquet/partição para reduzir o scan. Storage: item S3."],
        )


class AwsRedshiftCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_redshift",
        name="Amazon Redshift Serverless",
        category="Warehouse e consulta",
        provider="aws",
        description="Warehouse serverless (RPU-hora + managed storage).",
        fields=[
            FieldSchema(
                id="rpu_hours",
                label="RPU-horas",
                type="number",
                unit="RPU-hora/mês",
                default=120,
                min=0,
                help="Ex.: 8 RPU × 15 h = 120. Mínimo de cobrança 60 s.",
            ),
            FieldSchema(id="storage_gb", label="Managed storage", type="number", unit="GB", default=500, min=0),
        ],
        pricing_references=[to_reference(p.AWS_REDSHIFT_RPU), to_reference(p.AWS_REDSHIFT_STORAGE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [
            to_line_item(p.AWS_REDSHIFT_RPU, self.get_number(inputs, "rpu_hours")),
            to_line_item(p.AWS_REDSHIFT_STORAGE, self.get_number(inputs, "storage_gb")),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Clusters provisionados (RA3/DC2) usam outra tabela."],
        )


class AwsGlueCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_glue",
        name="AWS Glue",
        category="Processamento e Analytics",
        provider="aws",
        description="ETL Spark serverless (DPU-hora).",
        fields=[
            FieldSchema(id="dpu_hours", label="DPU-horas", type="number", unit="DPU-hora/mês", default=50, min=0),
        ],
        pricing_references=[to_reference(p.AWS_GLUE_DPU)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [to_line_item(p.AWS_GLUE_DPU, self.get_number(inputs, "dpu_hours"))]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Crawlers e Data Catalog têm franquia; jobs Flex são mais baratos."],
        )


class AwsKinesisCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_kinesis",
        name="Amazon Kinesis Data Streams",
        category="Ingestão e Streaming",
        provider="aws",
        description="Streaming provisionado (shards + PUT payload units).",
        fields=[
            FieldSchema(
                id="shard_hours",
                label="Shard-horas",
                type="number",
                unit="shard-hora/mês",
                default=730,
                min=0,
            ),
            FieldSchema(
                id="put_millions",
                label="PUT payload units",
                type="number",
                unit="milhões/mês",
                default=20,
                min=0,
                help="1 unit = 25 KB.",
            ),
        ],
        pricing_references=[to_reference(p.AWS_KINESIS_SHARD), to_reference(p.AWS_KINESIS_PUT)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [
            to_line_item(p.AWS_KINESIS_SHARD, self.get_number(inputs, "shard_hours")),
            to_line_item(p.AWS_KINESIS_PUT, self.get_number(inputs, "put_millions")),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["On-demand e Extended retention são outras tabelas."],
        )


class AwsFlinkCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_flink",
        name="Amazon Managed Service for Apache Flink",
        category="Ingestão e Streaming",
        provider="aws",
        description="Processamento e transformação de streams; separado do barramento Kinesis Data Streams.",
        fields=[
            FieldSchema(
                id="kpu_hours",
                label="KPU-horas",
                type="number",
                unit="KPU-hora/mês",
                default=1460,
                min=0,
                help="Inclua a KPU adicional usada pela aplicação.",
            ),
            FieldSchema(
                id="application_storage_gb",
                label="Storage da aplicação",
                type="number",
                unit="GB/mês",
                default=100,
                min=0,
            ),
        ],
        pricing_references=[to_reference(p.AWS_FLINK_KPU), to_reference(p.AWS_FLINK_STORAGE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [
            to_line_item(p.AWS_FLINK_KPU, self.get_number(inputs, "kpu_hours")),
            to_line_item(p.AWS_FLINK_STORAGE, self.get_number(inputs, "application_storage_gb")),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Kinesis Data Streams, S3 e backups duráveis são cobrados separadamente."],
        )


class AwsDmsCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_dms",
        name="AWS Database Migration Service",
        category="Ingestão e Streaming",
        provider="aws",
        description="CDC e carga de bancos para o lake/warehouse (instância dms.t3.medium).",
        fields=[
            FieldSchema(id="hours", label="Horas da instância", type="number", unit="hora/mês", default=730, min=0),
        ],
        pricing_references=[to_reference(p.AWS_DMS_INSTANCE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [to_line_item(p.AWS_DMS_INSTANCE, self.get_number(inputs, "hours"))]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Serverless DMS e storage de logs à parte."],
        )


class AwsDataSyncCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_datasync",
        name="AWS DataSync",
        category="Ingestão e Streaming",
        provider="aws",
        description="Cópia gerenciada on-prem/nuvem → S3/EFS/FSx.",
        fields=[
            FieldSchema(id="copied_gb", label="Dados copiados", type="number", unit="GB/mês", default=500, min=0),
        ],
        pricing_references=[to_reference(p.AWS_DATASYNC_GB)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [to_line_item(p.AWS_DATASYNC_GB, self.get_number(inputs, "copied_gb"))]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Egress da origem e storage de destino são cobrados à parte."],
        )


class AwsEmrCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_emr",
        name="Amazon EMR",
        category="Processamento e Analytics",
        provider="aws",
        description="Spark/Hadoop gerenciado — taxa EMR + instâncias EC2.",
        fields=[
            FieldSchema(
                id="instance_hours",
                label="Instância-horas (m5.xlarge)",
                type="number",
                unit="hora/mês",
                default=1460,
                min=0,
                help="Ex.: 2 nós × 730 h.",
            ),
        ],
        pricing_references=[to_reference(p.AWS_EMR_FEE), to_reference(p.AWS_EC2_M5_XLARGE)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        instance_hours = self.get_number(inputs, "instance_hours")
        line_items = [
            to_line_item(p.AWS_EMR_FEE, instance_hours),
            to_line_item(p.AWS_EC2_M5_XLARGE, instance_hours),
        ]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["EBS e transferência permanecem à parte. EMR Serverless usa DPU."],
        )


class AwsMwaaCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="aws_mwaa",
        name="Amazon MWAA",
        category="Orquestração",
        provider="aws",
        description="Apache Airflow gerenciado (ambiente mw1.small).",
        fields=[
            FieldSchema(id="hours", label="Horas do ambiente", type="number", unit="hora/mês", default=730, min=0),
        ],
        pricing_references=[to_reference(p.AWS_MWAA_ENV)],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        line_items = [to_line_item(p.AWS_MWAA_ENV, self.get_number(inputs, "hours"))]
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(sum(i.subtotal for i in line_items), 2),
            notes=["Schedulers/workers adicionais mudam o preço."],
        )
