-- One row per patient and target gene, including zero mutation counts.
WITH target_genes(gene_symbol) AS (
    VALUES
        ('TP53'),
        ('KRAS'),
        ('EGFR'),
        ('STK11'),
        ('KEAP1')
)
SELECT
    p.patient_id,
    tg.gene_symbol,
    COUNT(m.mutation_id) AS protein_altering_count
FROM patients AS p
CROSS JOIN target_genes AS tg
LEFT JOIN samples AS s
    ON s.patient_id = p.patient_id
LEFT JOIN mutations AS m
    ON m.sample_id = s.sample_id
   AND m.gene_symbol = tg.gene_symbol
   AND m.variant_classification <> 'Silent'
GROUP BY
    p.patient_id,
    tg.gene_symbol
ORDER BY
    p.patient_id,
    tg.gene_symbol;
