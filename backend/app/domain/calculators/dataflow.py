from __future__ import annotations

from app.data import pricing as p
from app.domain.calculators.base import BaseCalculator
from app.domain.calculators._pricing_utils import to_line_item, to_reference
from app.domain.schemas import CalculationResult, FieldOption, FieldSchema, ServiceDefinition

_GPU_OPTIONS = [
    FieldOption(value="none", label="Sem GPU"),
    FieldOption(value="t4", label="NVIDIA Tesla T4"),
    FieldOption(value="l4", label="NVIDIA Tesla L4"),
    FieldOption(value="p4", label="NVIDIA Tesla P4"),
    FieldOption(value="p100", label="NVIDIA Tesla P100"),
    FieldOption(value="v100", label="NVIDIA Tesla V100"),
    FieldOption(value="a100_40", label="NVIDIA A100 40 GB"),
    FieldOption(value="a100_80", label="NVIDIA A100 80 GB"),
    FieldOption(value="h100", label="NVIDIA H100"),
    FieldOption(value="h100_mega", label="NVIDIA H100 Mega"),
    FieldOption(value="rtx_pro_6000", label="NVIDIA RTX PRO 6000"),
]


class DataflowCalculator(BaseCalculator):
    definition = ServiceDefinition(
        id="dataflow",
        name="Dataflow",
        category="Processamento e Analytics",
        description="Processamento de dados em lote e streaming (Apache Beam gerenciado): Classic ou Prime.",
        fields=[
            FieldSchema(
                id="edition",
                label="Edição",
                type="select",
                default="classic",
                options=[
                    FieldOption(value="classic", label="Dataflow Classic (vCPU, memória, Shuffle/SE)"),
                    FieldOption(value="prime", label="Dataflow Prime (Data Compute Units)"),
                ],
            ),
            FieldSchema(
                id="job_type",
                label="Tipo de job",
                type="select",
                default="streaming",
                options=[
                    FieldOption(value="streaming", label="Streaming"),
                    FieldOption(value="batch", label="Batch"),
                    FieldOption(value="flexrs", label="FlexRS (batch com desconto ~40%)"),
                ],
                help="FlexRS só existe no Classic. No Prime, FlexRS é tratado como batch DCU.",
            ),
            FieldSchema(
                id="job_hours",
                label="Horas de execução do job",
                type="number",
                unit="hora/mês",
                default=730,
                min=0,
                help="Soma das horas em que workers ficam ligados no mês.",
            ),
            FieldSchema(
                id="worker_nodes",
                label="Número de workers",
                type="number",
                unit="workers",
                default=1,
                min=0,
                help="Média (ou máximo, para disco). FlexRS exige no mínimo 2.",
            ),
            FieldSchema(
                id="streaming_engine_compute_units",
                label="Streaming Engine Compute Units",
                type="number",
                unit="unidade-hora/mês",
                default=0,
                min=0,
                help="Cobrança por recurso (não legado). Só streaming. No Prime vira DCU.",
            ),
            FieldSchema(
                id="streaming_engine_data_gib",
                label="Streaming Engine data processed (legado)",
                type="number",
                unit="GiB/mês",
                default=0,
                min=0,
                help="Modelo antigo por volume. Use 0 se a cobrança for por Compute Units.",
            ),
            FieldSchema(
                id="cud",
                label="Committed use discount (CUD)",
                type="select",
                default="none",
                options=[
                    FieldOption(value="none", label="Sem compromisso (on-demand)"),
                    FieldOption(value="cud_1y", label="CUD 1 ano (~20% no streaming)"),
                    FieldOption(value="cud_3y", label="CUD 3 anos (~40% no streaming)"),
                ],
                help="CUD da tabela oficial aplica a streaming (vCPU, memória, SE e DCU Prime). Batch/FlexRS não têm CUD nessa tabela.",
            ),
            FieldSchema(
                id="gpu_model",
                label="GPU — modelo",
                type="select",
                default="none",
                options=_GPU_OPTIONS,
                help="Mesmo preço para batch e streaming. FlexRS não suporta GPU.",
            ),
            FieldSchema(
                id="gpu_count",
                label="GPU — quantidade",
                type="number",
                unit="GPUs por worker",
                default=0,
                min=0,
            ),
        ],
        pricing_references=[
            to_reference(price)
            for price in [
                p.DATAFLOW_BATCH_VCPU,
                p.DATAFLOW_BATCH_MEMORY,
                p.DATAFLOW_FLEXRS_VCPU,
                p.DATAFLOW_STREAMING_RATES["none"]["vcpu"],
                p.DATAFLOW_STREAMING_RATES["none"]["secu"],
                p.DATAFLOW_STREAMING_RATES["none"]["legacy_data"],
                p.DATAFLOW_PRIME_DCU_BATCH,
                p.DATAFLOW_PRIME_DCU_STREAMING["none"],
                p.DATAFLOW_PD,
                *p.DATAFLOW_GPU_PRICES.values(),
            ]
        ],
    )

    def calculate(self, inputs: dict[str, float | str]) -> CalculationResult:
        edition = self.get_string(inputs, "edition", "classic")
        job_type = self.get_string(inputs, "job_type", "streaming")
        cud = self.get_string(inputs, "cud", "none")
        if cud not in p.DATAFLOW_STREAMING_RATES:
            cud = "none"

        job_hours = self.get_number(inputs, "job_hours")
        workers = max(0.0, self.get_number(inputs, "worker_nodes"))
        secu = self.get_number(inputs, "streaming_engine_compute_units")
        legacy_gib = self.get_number(inputs, "streaming_engine_data_gib")
        gpu_model = self.get_string(inputs, "gpu_model", "none")
        gpu_count = self.get_number(inputs, "gpu_count")

        notes: list[str] = []
        if job_type == "flexrs" and edition == "prime":
            notes.append("FlexRS não está disponível no Dataflow Prime; o cálculo usa DCU de batch.")
            job_type_for_prime = "batch"
        else:
            job_type_for_prime = job_type if job_type != "flexrs" else "batch"

        if job_type == "flexrs":
            workers = max(workers, 2.0)

        shape_key = job_type if job_type in p.DATAFLOW_WORKER_DEFAULTS else "streaming"
        shape = p.DATAFLOW_WORKER_DEFAULTS[shape_key]
        disk_gb = shape["disk_gb"]
        if job_type == "streaming" and (secu > 0 or legacy_gib > 0):
            disk_gb = p.DATAFLOW_STREAMING_ENGINE_DISK_GB

        vcpu_hours = job_hours * workers * shape["vcpu"]
        memory_hours = job_hours * workers * shape["memory_gb"]
        disk_hours = job_hours * workers * disk_gb
        line_items = []

        if edition == "prime":
            dcu = job_hours * workers * max(shape["vcpu"], shape["memory_gb"] / 4.0)
            if job_type_for_prime == "streaming":
                dcu += secu
                line_items.append(to_line_item(p.DATAFLOW_PRIME_DCU_STREAMING[cud], dcu))
                notes.append(
                    "Prime streaming: DCU estima workers (1 DCU ≈ 1 vCPU·hora em máquina 4 GiB) "
                    "e soma as Streaming Engine Compute Units."
                )
            else:
                line_items.append(to_line_item(p.DATAFLOW_PRIME_DCU_BATCH, dcu))
                if cud != "none":
                    notes.append("CUD de streaming não se aplica a DCU batch na tabela oficial.")
            if legacy_gib > 0:
                notes.append("Data processed legado não entra no Prime; use Classic ou Compute Units.")
        else:
            if job_type == "batch":
                line_items.extend(
                    [
                        to_line_item(p.DATAFLOW_BATCH_VCPU, vcpu_hours),
                        to_line_item(p.DATAFLOW_BATCH_MEMORY, memory_hours),
                    ]
                )
            elif job_type == "flexrs":
                line_items.extend(
                    [
                        to_line_item(p.DATAFLOW_FLEXRS_VCPU, vcpu_hours),
                        to_line_item(p.DATAFLOW_FLEXRS_MEMORY, memory_hours),
                    ]
                )
                notes.append("FlexRS: vCPU e memória com desconto uniforme de ~40%. Disco e Shuffle não têm esse desconto.")
            else:
                rates = p.DATAFLOW_STREAMING_RATES[cud]
                line_items.extend(
                    [
                        to_line_item(rates["vcpu"], vcpu_hours),
                        to_line_item(rates["memory"], memory_hours),
                    ]
                )
                if secu > 0:
                    line_items.append(to_line_item(rates["secu"], secu))
                if legacy_gib > 0:
                    line_items.append(to_line_item(rates["legacy_data"], legacy_gib))

        line_items.append(to_line_item(p.DATAFLOW_PD, disk_hours))

        if gpu_model != "none" and gpu_count > 0:
            if job_type == "flexrs":
                notes.append("FlexRS não suporta GPU; a linha de GPU foi omitida.")
            elif gpu_model in p.DATAFLOW_GPU_PRICES:
                gpu_hours = job_hours * workers * gpu_count
                line_items.append(to_line_item(p.DATAFLOW_GPU_PRICES[gpu_model], gpu_hours))

        notes.append(
            f"Formato do worker ({shape_key}): {shape['vcpu']:g} vCPU, "
            f"{shape['memory_gb']:g} GiB RAM, {disk_gb:g} GiB PD (padrões da página de pricing)."
        )

        total = sum(item.subtotal for item in line_items)
        return CalculationResult(
            service_id=self.definition.id,
            line_items=line_items,
            total=round(total, 2),
            notes=notes,
        )
