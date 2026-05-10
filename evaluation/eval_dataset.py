from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvalSample:
    question: str
    ground_truth: str
    contexts: list[str] = field(default_factory=list)


EVAL_DATASET: list[EvalSample] = [
    EvalSample(
        question="What evidence does G-BA require for added benefit assessment of oncology drugs under AMNOG?",
        ground_truth=(
            "G-BA requires the manufacturer to submit a dossier demonstrating added benefit compared to "
            "the appropriate comparator (zweckmäßige Vergleichstherapie, ZVT) set by G-BA. The dossier "
            "must include patient-relevant endpoints such as overall survival, progression-free survival, "
            "response rates, health-related quality of life, and adverse events. The benefit must be "
            "shown primarily from randomised controlled trials; indirect comparisons are accepted if "
            "head-to-head data against the ZVT are unavailable. G-BA categorises benefit into six tiers: "
            "major added benefit (erheblicher Zusatznutzen), considerable, minor, non-quantifiable, "
            "no added benefit proven, and less benefit."
        ),
        contexts=[
            (
                "Under AMNOG (Arzneimittelmarktneuordnungsgesetz), the manufacturer must file a benefit "
                "dossier within three months of market entry. The zweckmäßige Vergleichstherapie (ZVT), "
                "or appropriate comparator, is defined by G-BA prior to approval and typically reflects "
                "standard of care. The dossier must present patient-relevant outcomes including overall "
                "survival (OS), progression-free survival (PFS), quality of life (QoL), and adverse events "
                "from randomised controlled clinical trials."
            ),
            (
                "G-BA classifies added benefit into six categories: erheblicher Zusatznutzen (major), "
                "beträchtlicher (considerable), geringer (minor), nicht quantifizierbarer (non-quantifiable), "
                "kein Beleg für Zusatznutzen (no proven added benefit), and geringerer Nutzen (less benefit). "
                "In oncology, surrogate endpoints like PFS may be accepted when validated correlation with OS "
                "has been established, but G-BA generally prefers final endpoints."
            ),
            (
                "When data against the ZVT are not available from head-to-head RCTs, the manufacturer may "
                "submit indirect treatment comparisons (ITCs) or network meta-analyses (NMAs). However, "
                "G-BA systematically downgrades evidence certainty for indirect comparisons, often resulting "
                "in a lower benefit category. Real-world evidence is generally not accepted as primary evidence "
                "for AMNOG assessments."
            ),
            (
                "Patient-relevant endpoints required in AMNOG dossiers include overall survival (OS), "
                "progression-free survival (PFS), response rates (tumour response), health-related quality "
                "of life (HRQoL), and adverse events including serious adverse events and discontinuations. "
                "Response rates are considered intermediate endpoints and must be accompanied by evidence "
                "of their clinical relevance."
            ),
        ],
    ),
    EvalSample(
        question="How does NICE define the cost-effectiveness threshold for technology appraisals?",
        ground_truth=(
            "NICE uses a cost-per-QALY (Quality-Adjusted Life Year) gained threshold of £20,000–£30,000 "
            "as the standard range for technology appraisals. Treatments priced above £30,000 per QALY "
            "require stronger evidence of benefit. For end-of-life treatments meeting specific criteria "
            "(short remaining life expectancy, meaningful extension of life), a higher threshold of up to "
            "£50,000 per QALY may apply. For highly specialised technologies (HST) for very rare diseases, "
            "the threshold can extend up to £100,000 per QALY."
        ),
        contexts=[
            (
                "NICE technology appraisals use cost-utility analysis expressed as incremental cost-effectiveness "
                "ratio (ICER) in cost per QALY gained. The standard threshold range is £20,000–£30,000 per QALY. "
                "Technologies below £20,000/QALY are almost always recommended; those above £30,000/QALY "
                "face a higher evidence burden."
            ),
            (
                "Under the end-of-life criteria, treatments may be considered at up to approximately £50,000 "
                "per QALY if: the condition has a short life expectancy (typically under 24 months), and the "
                "treatment offers a meaningful extension of life (at least 3 additional months on average). "
                "EQ-5D is the preferred utility measure for QALY estimation."
            ),
            (
                "Highly Specialised Technologies (HST) programme applies to drugs for very rare conditions "
                "(prevalence typically < 1 in 50,000). The cost-effectiveness threshold can extend up to "
                "£100,000 per QALY, reflecting the unmet need, societal value, and limitations of evidence "
                "in ultra-rare diseases."
            ),
        ],
    ),
    EvalSample(
        question="What are the SMR and ASMR ratings used by HAS in France and what do they mean?",
        ground_truth=(
            "HAS uses two ratings: SMR (Service Médical Rendu — Clinical Benefit) and ASMR "
            "(Amélioration du SMR — Improvement in Clinical Benefit). SMR has four levels: "
            "important (I), moderate (II), low (III), and insufficient (IV — no reimbursement). "
            "SMR determines whether a drug is reimbursed and at what rate (SMR Important = 65%; "
            "Modéré = 30%; Faible = 15%). ASMR is a five-level scale (I–V) measuring the added "
            "clinical benefit over existing treatments: I = major improvement, II = significant, "
            "III = moderate, IV = minor, V = no improvement. ASMR influences price negotiation "
            "with the CEPS (Economic Committee for Health Products)."
        ),
        contexts=[
            (
                "The Transparency Committee (Commission de la Transparence) of HAS evaluates drugs for "
                "reimbursement using two key metrics: Service Médical Rendu (SMR — Clinical Benefit) and "
                "Amélioration du Service Médical Rendu (ASMR — Improvement in Clinical Benefit). "
                "SMR reflects the intrinsic clinical benefit and is rated Important, Modéré (Moderate), "
                "Faible (Low), or Insuffisant (Insufficient). Only drugs with SMR Important, Modéré, or "
                "Faible are reimbursed; SMR Insuffisant leads to refusal."
            ),
            (
                "Reimbursement rates in France are linked to SMR level: SMR Important = 65%, SMR Modéré = 30%, "
                "SMR Faible = 15%. For severe diseases without adequate treatments, SMR Important drugs may "
                "be reimbursed at 100%."
            ),
            (
                "ASMR (Amélioration du SMR) rates clinical added value on a I–V scale: ASMR I (major "
                "improvement), ASMR II (significant improvement), ASMR III (moderate improvement), ASMR IV "
                "(minor improvement), ASMR V (no improvement demonstrated). ASMR I–III support premium "
                "pricing in negotiations with the CEPS. ASMR V drugs are priced at or below existing "
                "comparators."
            ),
        ],
    ),
    EvalSample(
        question="What safety signals are associated with GLP-1 receptor agonists in European regulatory filings?",
        ground_truth=(
            "GLP-1 receptor agonists are associated with several safety signals documented in EU regulatory "
            "filings: gastrointestinal adverse events (nausea, vomiting, diarrhoea) are the most common, "
            "particularly at treatment initiation. Pancreatitis is a serious signal under monitoring. "
            "Thyroid C-cell tumours (medullary thyroid carcinoma) are a theoretical risk observed in rodent "
            "studies; the clinical relevance in humans is unknown. EMA has issued guidance on monitoring "
            "suicidal ideation and self-harm signals. Diabetic retinopathy worsening has been observed with "
            "rapid glycaemic improvement from semaglutide. Acute kidney injury has been reported secondary "
            "to GI-related dehydration."
        ),
        contexts=[
            (
                "GLP-1 receptor agonists (liraglutide, semaglutide, dulaglutide, exenatide) share a class "
                "safety profile. The most frequent adverse events are gastrointestinal: nausea incidence of "
                "20–40% in registration trials, vomiting, and diarrhoea. These effects are dose-dependent "
                "and dose-escalation strategies reduce discontinuation rates."
            ),
            (
                "EMA's safety committee (PRAC) reviewed signals of suicidal ideation and self-harm for "
                "GLP-1 agonists in 2023 following reports post-marketing. For semaglutide (Ozempic, "
                "Wegovy) and liraglutide (Victoza, Saxenda), the review concluded that available evidence "
                "does not support a causal relationship, but enhanced pharmacovigilance continues."
            ),
            (
                "Pancreatitis is listed as an important identified risk in the risk management plans (RMPs) "
                "of all approved GLP-1 receptor agonists in Europe. Patients with prior history of "
                "pancreatitis should be treated with caution. Medullary thyroid carcinoma (MTC) risk, "
                "though observed in rodent carcinogenicity studies, has not been confirmed in human data "
                "from cardiovascular outcomes trials (LEADER, SUSTAIN-6, REWIND)."
            ),
            (
                "Additional safety signals for GLP-1 receptor agonists include diabetic retinopathy "
                "worsening observed with rapid glycaemic improvement particularly with semaglutide, "
                "and acute kidney injury reported secondary to GI-related dehydration. Thyroid C-cell "
                "tumours are a theoretical risk seen in rodent studies; clinical relevance in humans "
                "remains unknown based on current evidence."
            ),
        ],
    ),
    EvalSample(
        question="What is the EMA's PRIME scheme and which therapeutic areas benefit most from it?",
        ground_truth=(
            "PRIME (PRIority MEdicines) is an EMA scheme launched in 2016 to enhance support for the "
            "development of medicines targeting an unmet medical need. PRIME provides early and proactive "
            "EMA scientific support, including advice on clinical trial design, endpoints, and benefit-risk "
            "framing. Eligible medicines must show preliminary clinical evidence of substantial improvement "
            "over existing treatment or address a condition with no satisfactory therapy. The scheme is "
            "particularly beneficial for oncology, rare diseases, infectious diseases, neurology, and "
            "metabolic disorders. PRIME designation also facilitates parallel EMA-HTA scientific advice."
        ),
        contexts=[
            (
                "The PRIME scheme (PRIority MEdicines) was established by EMA in 2016 to support development "
                "of medicines addressing unmet medical needs. PRIME provides early and proactive EMA scientific "
                "support, including advice on clinical trial design, endpoints, and benefit-risk framing. "
                "A dedicated EMA contact point and enhanced scientific dialogue during development are provided, "
                "along with accelerated assessment at the time of marketing authorisation application. "
                "The scheme is open to developers of any size, including SMEs, academia, and not-for-profit organisations."
            ),
            (
                "PRIME eligibility criteria: the medicine must target a condition for which there is no "
                "satisfactory treatment, OR offer a major therapeutic advantage over existing treatments. "
                "Preliminary clinical evidence is required (phase I data minimum). In the rare disease "
                "space, orphan designation complements PRIME eligibility."
            ),
            (
                "Therapeutic areas receiving most PRIME designations include oncology (approximately 30%), "
                "rare diseases (25%), infectious diseases including HIV and HCV (15%), neurological "
                "conditions, and metabolic disorders. PRIME allows parallel scientific advice with HTA bodies, "
                "reducing the timeline between EMA approval and national reimbursement decisions."
            ),
        ],
    ),
    EvalSample(
        question="What are the reimbursement conditions for CAR-T therapies in Germany under the AMNOG process?",
        ground_truth=(
            "CAR-T therapies (e.g. axicabtagene ciloleucel, tisagenlecleucel) in Germany undergo the "
            "standard AMNOG benefit assessment. Due to their high acquisition cost and single-administration "
            "nature, they typically receive considerable or major added benefit ratings in their approved "
            "indications (relapsed/refractory large B-cell lymphoma, ALL) where they represent the only "
            "option. Price negotiations with the GKV-Spitzenverband follow. Some CAR-T products are subject "
            "to hospital-only supply restrictions. Outcomes-based managed entry agreements (MEAs) have been "
            "explored to mitigate payer uncertainty around long-term durability."
        ),
        contexts=[
            (
                "CAR-T cell therapies approved in Europe include axicabtagene ciloleucel (Yescarta), "
                "tisagenlecleucel (Kymriah), lisocabtagene maraleucel (Breyanzi), and idecabtagene vicleucel "
                "(Abecma). Under AMNOG, each undergoes early benefit assessment upon German market entry. "
                "G-BA has classified these therapies as providing 'beträchtlicher Zusatznutzen' (considerable "
                "added benefit) in relapsed/refractory settings where no curative alternative exists."
            ),
            (
                "The high price of CAR-T therapies (typically €300,000–€400,000 per treatment) creates "
                "significant negotiation tension. Following AMNOG assessment, the GKV-Spitzenverband "
                "negotiates a reimbursement amount. Outcomes-based reimbursement models linking payment "
                "to durable response (e.g. payment by instalment over 3 years tied to maintained remission) "
                "are increasingly discussed but complex to implement in the German system."
            ),
            (
                "CAR-T therapies are subject to hospital exemption rules in Germany and must be administered "
                "in certified centres. JACIE accreditation may be required. Some products are Section 129c "
                "hospital pharmacy preparations, affecting reimbursement routes."
            ),
            (
                "CAR-T therapies including tisagenlecleucel (Kymriah) are approved for relapsed/refractory "
                "acute lymphoblastic leukaemia (ALL) in paediatric and young adult patients. G-BA assessments "
                "have resulted in both beträchtlicher Zusatznutzen (considerable added benefit) and erheblicher "
                "Zusatznutzen (major added benefit) ratings depending on the specific indication and whether "
                "the CAR-T represents the only curative option. The single-administration nature of CAR-T "
                "therapies distinguishes them from chronic treatments in terms of pricing and payer risk."
            ),
        ],
    ),
    EvalSample(
        question="How does NICE handle technology appraisals for rare diseases differently from standard TAs?",
        ground_truth=(
            "NICE operates two pathways for rare diseases: the standard Technology Appraisal (TA) process "
            "and the Highly Specialised Technologies (HST) programme. The HST programme applies to "
            "treatments for conditions affecting fewer than 1 in 50,000 people. HST uses a more flexible "
            "cost-effectiveness threshold (up to £100,000 per QALY) and a modified economic modelling "
            "approach that places greater weight on wider societal value. Single-arm trial data and "
            "real-world evidence may be more readily accepted given small patient populations. The Rare "
            "Diseases Advisory Group (RDAG) provides additional expertise."
        ),
        contexts=[
            (
                "NICE's Highly Specialised Technologies (HST) programme evaluates medicines for very rare, "
                "typically life-threatening conditions affecting a very small number of patients in England "
                "(usually fewer than 500 patients per year). The cost-effectiveness threshold for HST "
                "is up to £100,000 per QALY, compared to £20,000–£30,000 for standard TAs."
            ),
            (
                "In HST appraisals, NICE accepts greater flexibility in evidence: single-arm trials, "
                "patient registry data, and extrapolations from surrogate endpoints are more commonly "
                "used because large RCTs are often infeasible. The Equal Access to Medicines Regulatory "
                "Framework (EAMR) ensures these products can still reach patients with unmet needs."
            ),
            (
                "The 'value of hope' and rarity modifiers mean that NICE gives additional weight to "
                "medicines that address life-threatening conditions where patients have no alternatives. "
                "Budget impact is separately assessed: for drugs costing over £20 million annually, "
                "a separate commercial discussion with NHS England may be required."
            ),
            (
                "The HST programme applies to treatments for conditions affecting fewer than 1 in 50,000 "
                "people. The Rare Diseases Advisory Group (RDAG) provides additional expertise to support "
                "NICE appraisal committees in evaluating evidence for ultra-rare diseases, including "
                "assessment of single-arm trials and real-world evidence."
            ),
        ],
    ),
    EvalSample(
        question="What clinical endpoints does EMA accept for oncology drug approvals in the post-2020 era?",
        ground_truth=(
            "EMA accepts a range of clinical endpoints for oncology approvals. Overall survival (OS) "
            "remains the gold standard. Progression-free survival (PFS) is accepted as a primary endpoint "
            "when a validated OS correlation exists or when OS data are immature. Overall response rate (ORR) "
            "and duration of response (DoR) can support conditional marketing authorisation. Minimal residual "
            "disease (MRD) negativity has been accepted in haematological malignancies. Patient-reported "
            "outcomes (PROs) for HRQoL are increasingly required. Event-free survival (EFS) is used in "
            "paediatric oncology. EMA requires pre-specified statistical analysis plans and addresses "
            "multiple testing carefully."
        ),
        contexts=[
            (
                "EMA's guidance on clinical trials in small populations and oncology (EMEA/CHMP/EWP/205/95) "
                "establishes the hierarchy of endpoints. OS is the most reliable evidence of clinical benefit. "
                "PFS is accepted when the treatment effect on OS is unlikely to be demonstrable due to trial "
                "design, confounding by subsequent therapies, or event immaturity."
            ),
            (
                "Conditional marketing authorisations (CMA) in oncology may be granted based on ORR and DoR "
                "from single-arm trials when the unmet need is high and results are substantial. Post-approval, "
                "confirmatory data are required within the specific obligation timeline."
            ),
            (
                "MRD (minimal residual disease) negativity as a surrogate has been accepted by EMA in "
                "multiple myeloma and acute lymphoblastic leukaemia in recent approvals. EMA's Oncology "
                "Working Group coordinates guidance on novel biomarker-based endpoints and basket/umbrella "
                "trial designs."
            ),
            (
                "Event-free survival (EFS) is used as a primary endpoint in paediatric oncology approvals "
                "where OS data are too immature. EMA requires pre-specified statistical analysis plans "
                "(SAPs) before unblinding and careful handling of multiple testing through pre-defined "
                "hierarchical testing procedures to control type I error."
            ),
        ],
    ),
    EvalSample(
        question="What types of evidence are accepted by AIFA for drug reimbursement in Italy?",
        ground_truth=(
            "AIFA evaluates drugs for reimbursabilità (reimbursement) based on clinical and health economic "
            "evidence. Preferred evidence includes RCT data demonstrating superiority or non-inferiority vs. "
            "standard of care on clinically meaningful endpoints. AIFA uses the innovative drug (farmaco "
            "innovativo) classification for truly innovative therapies, which triggers priority reimbursement "
            "and ring-fenced budget. Budget impact analysis is mandatory. AIFA requires post-marketing "
            "registries (registri AIFA) for high-cost drugs, enabling outcomes-based payment and real-world "
            "monitoring. Managed entry agreements (MEAs) including cost-sharing, payment-by-results, and "
            "risk-sharing are widely used."
        ),
        contexts=[
            (
                "AIFA's Technical and Scientific Commission (CTS) evaluates marketing authorisations and "
                "Pricing and Reimbursement Committee (CPR) negotiates the price. For reimbursement, AIFA "
                "classifies drugs into Classe A (fully reimbursed), Classe H (hospital only), or Classe C "
                "(patient pays). Innovation classification (terapeutica, nosologica, or processuale) "
                "unlocks a dedicated ring-fenced innovation fund, providing priority reimbursement "
                "separate from the general pharmaceutical budget."
            ),
            (
                "AIFA operates one of Europe's most developed systems for outcomes-based pricing using "
                "registri AIFA — mandatory real-world registries for high-cost drugs. Data collected in "
                "registries inform payment-by-results (PBR) agreements: payment is made only if the patient "
                "achieves the predefined clinical outcome. MEAs also include cost-sharing (patient pays "
                "a fraction if treatment fails) and risk-sharing arrangements."
            ),
            (
                "Budget impact analysis (analisi di impatto sul budget) is mandatory for all drugs "
                "seeking reimbursement with AIFA, covering a 3-year time horizon for the National "
                "Health Service (SSN) budget. AIFA negotiated prices are typically among the lowest "
                "in the Big-5 EU markets due to Italy's GDP and reference pricing from lower-cost "
                "countries. Parallel trade is a significant concern for multinational manufacturers."
            ),
        ],
    ),
    EvalSample(
        question="What is the role of indirect treatment comparisons in HTA submissions across EU agencies?",
        ground_truth=(
            "Indirect treatment comparisons (ITCs) and network meta-analyses (NMAs) are used when "
            "direct head-to-head RCT data against the relevant comparator are unavailable. Their "
            "acceptance varies by agency: NICE has an established framework for NMAs in decision models "
            "and generally accepts well-conducted ITCs with appropriate uncertainty quantification. "
            "G-BA is the most restrictive — ITCs are accepted but typically result in a lower benefit "
            "category, and adjusted indirect comparisons may be rejected if heterogeneity is high. "
            "HAS accepts ITCs but assesses their methodological quality rigorously. EMA may accept ITCs "
            "for market authorisation in orphan diseases. NICE Decision Support Unit (DSU) publishes "
            "technical support documents on NMA methodology."
        ),
        contexts=[
            (
                "Network meta-analysis (NMA) allows simultaneous comparison of multiple treatments using "
                "a connected evidence network. Assumptions of transitivity and consistency must be met. "
                "NICE DSU Technical Support Documents 2 and 3 provide guidance on evidence synthesis "
                "methods for decision-making. Bayesian NMA is the preferred framework for NICE submissions."
            ),
            (
                "G-BA has historically been the most restrictive in accepting indirect comparisons under "
                "AMNOG. If the dossier relies on adjusted indirect comparisons (MAIC/STC) or NMA as primary "
                "evidence, G-BA typically considers evidence certainty 'not proven' or reduces the benefit "
                "category. Population differences between trials (heterogeneity) are frequently cited "
                "as a reason for reduced benefit classification."
            ),
            (
                "HAS evaluates indirect comparisons using a structured quality assessment approach. "
                "Key criteria: appropriateness of the comparator network, statistical heterogeneity, "
                "similarity of study populations, and time horizon of follow-up. ASMR ratings based "
                "solely on indirect evidence are typically ASMR IV (minor improvement) or V "
                "(no demonstrated improvement). EMA may accept ITCs as primary evidence for market "
                "authorisation in orphan diseases where head-to-head trial data are unavailable."
            ),
        ],
    ),
    EvalSample(
        question="How are biosimilars evaluated for EU market access compared to originators?",
        ground_truth=(
            "Biosimilars undergo an abbreviated regulatory pathway at EMA, requiring a comparability "
            "exercise (analytical, non-clinical, clinical) that demonstrates similarity to the reference "
            "biologic. Clinical equivalence trials are not required if in vitro and PK/PD data confirm "
            "biosimilarity. For market access, most EU countries apply automatic substitution rules for "
            "biosimilars after the first prescription period, though policies vary. HTA bodies generally "
            "do not conduct full HTA for biosimilars given the reference product's established benefit; "
            "reimbursement follows the originator's category. Biosimilars typically trigger mandatory "
            "price reductions of 20–40% in most EU markets."
        ),
        contexts=[
            (
                "EMA biosimilar guidelines (EMEA/CHMP/BMWP/42832/2005 Rev1) require stepwise comparability: "
                "state-of-the-art analytical characterisation, non-clinical studies as needed, and targeted "
                "clinical studies focusing on PK/PD similarity and immunogenicity. Efficacy equivalence "
                "trials are not always required if PK similarity is established in a sensitive indication."
            ),
            (
                "EU biosimilar market access: most countries use INN prescribing or branded prescribing with "
                "automatic dispensing of biosimilars at pharmacy level. Germany (substitution prohibited at "
                "pharmacy without physician consent), France (interchangeability allowed after a stable "
                "period), and Italy use different models. The European Biosimilar Medicines Alliance "
                "advocates for prescriber-driven substitution."
            ),
            (
                "Biosimilar pricing policies across EU: mandatory price reductions at entry vary from 15% "
                "(some EU markets) to 30–40% (Scandinavia, Netherlands) below the originator price, with "
                "most markets seeing reductions of 20–40%. Tender "
                "systems (Netherlands CBG-monitored tenders, UK NHSE framework agreements) drive further "
                "price competition. Some biosimilars are priced below INN reference price lists."
            ),
            (
                "HTA bodies across the EU generally do not conduct a full health technology assessment for "
                "biosimilars, given that the reference product's clinical benefit is already established. "
                "Reimbursement is typically granted under the same category as the originator, and "
                "assessment focuses on price and budget impact rather than clinical effectiveness."
            ),
        ],
    ),
    EvalSample(
        question="What are the requirements for paediatric investigation plans (PIPs) under EU regulation?",
        ground_truth=(
            "The EU Paediatric Regulation (EC 1901/2006) requires all new medicines (and some existing ones) "
            "to comply with an agreed Paediatric Investigation Plan (PIP) before receiving a marketing "
            "authorisation, unless a waiver or deferral is granted. PIPs must be agreed with EMA's Paediatric "
            "Committee (PDCO) and cover studies in all relevant age groups. PIP compliance is mandatory even "
            "if the paediatric indication is not sought for the product. Successful completion of a PIP "
            "grants a 6-month extension of patent protection (Supplementary Protection Certificate). "
            "PUMA (paediatric-use marketing authorisation) is available for off-patent drugs."
        ),
        contexts=[
            (
                "EMA's Paediatric Committee (PDCO) is responsible for scientific aspects of paediatric "
                "medicines in the EU. Under EU Regulation (EC) No 1901/2006 (the Paediatric Regulation), "
                "applicants must submit a PIP application early in development and obtain PDCO agreement "
                "before filing a marketing authorisation application. PIP compliance is mandatory even if "
                "the applicant does not seek a paediatric indication — failure to comply results in refusal "
                "of the marketing authorisation. PIPs specify required age-group studies, formulations, and "
                "pharmacokinetic/safety endpoints for children (preterm neonate to adolescent, 0–17 years)."
            ),
            (
                "Waivers from PIP requirements are granted when the condition does not occur in children "
                "or when the medicine is likely to be ineffective or unsafe in paediatric patients. "
                "Deferrals allow marketing authorisation first in adults while paediatric studies are "
                "completed later. Class waivers cover entire classes of medicines with no paediatric use."
            ),
            (
                "The 6-month SPC (Supplementary Protection Certificate) extension reward for PIP compliance "
                "represents considerable commercial value for innovative medicines. The PUMA path (off-patent) "
                "allows 10-year data exclusivity for a new paediatric-specific marketing authorisation "
                "of an off-patent medicine successfully completing a PIP."
            ),
        ],
    ),
    EvalSample(
        question="How does the EU HTA Regulation (EU 2021/2282) change market access timelines for medicines?",
        ground_truth=(
            "The EU HTA Regulation, applicable from January 2025 for oncology and ATMPs, mandates joint "
            "clinical assessments (JCAs) conducted by the HTA Coordination Group (HTAGG) at the EU level. "
            "These assessments focus on relative effectiveness (comparative clinical benefit) and are "
            "non-binding — member states retain the right to make their own national reimbursement decisions "
            "based on local economic, social, and ethical criteria. The regulation aims to reduce duplication "
            "of clinical evidence assessment across 27 member states, theoretically saving 2–4 years of "
            "separate national HTA processes. National HTA bodies must use the JCA but can supplement it "
            "with national economic analyses."
        ),
        contexts=[
            (
                "EU Regulation 2021/2282 on Health Technology Assessment entered into force in January 2022 "
                "with a 3-year transition. From January 2025, joint clinical assessments (JCAs) are mandatory "
                "for all new oncology medicines and advanced therapy medicinal products (ATMPs) receiving "
                "centralised marketing authorisation. Scope expands to other therapeutic areas from 2028."
            ),
            (
                "The HTA Coordination Group (HTAGG), comprising all 27 EU member states plus EEA-EFTa "
                "observers, conducts JCAs. The assessment output is a common relative effectiveness "
                "assessment (REA) report covering the added clinical value vs. comparator. Economic "
                "assessments, pricing, and reimbursement decisions remain entirely national."
            ),
            (
                "For manufacturers, the EU HTA Regulation requires a single evidence submission at EMA "
                "approval time, including clinical dossier data formatted per PICO (Population, "
                "Intervention, Comparator, Outcomes) agreed with HTAGG. Early dialogue with HTAGG is "
                "available to align clinical development programs with joint assessment requirements."
            ),
            (
                "By replacing 27 separate national clinical HTA assessments with a single EU-level JCA, "
                "the regulation is expected to save 2–4 years from the typical sequence of national "
                "HTA processes. National HTA bodies must use the JCA output but retain the right to "
                "supplement it with their own national economic analyses and local value frameworks "
                "when making final reimbursement decisions."
            ),
        ],
    ),
    EvalSample(
        question="What is the ASMR V rating at HAS and how does it impact pricing in France?",
        ground_truth=(
            "ASMR V (Amélioration du Service Médical Rendu V) indicates no demonstrated improvement "
            "in clinical benefit over existing treatments. This is the lowest ASMR category. An ASMR V "
            "rating means the drug offers no therapeutic added value and its price must be at or below "
            "the least expensive comparator identified by HAS. The CEPS (Economic Committee for Health "
            "Products) negotiates prices with this benchmark ceiling. ASMR V drugs are still reimbursed "
            "if they have an SMR rating of Important, Modéré, or Faible — they simply cannot command "
            "a premium. This rating effectively limits commercial differentiation for 'me-too' drugs."
        ),
        contexts=[
            (
                "ASMR V is the lowest ASMR category and indicates no demonstrated improvement "
                "in clinical benefit over existing treatments. It is assigned by HAS when the medicine "
                "does not demonstrate superiority over the most appropriate comparator on any relevant "
                "clinical endpoint. An ASMR V rating means the drug offers no therapeutic added value. "
                "This rating is common for drugs entering a crowded therapeutic class or with insufficient "
                "comparative data. In 2022, approximately 55% of new drugs assessed by HAS received ASMR V. "
                "ASMR V drugs are still reimbursed provided the drug holds an SMR rating of Important, "
                "Modéré, or Faible — they simply cannot command a premium price over existing comparators."
            ),
            (
                "Pricing implications of ASMR V: the CEPS negotiates a price that must not exceed the "
                "lowest price of the existing comparators in France and cannot exceed the price of the "
                "same product in the four reference countries (Germany, UK, Spain, Italy). European "
                "reference pricing effectively compresses ASMR V prices to market levels."
            ),
            (
                "Manufacturers sometimes request reassessment (réévaluation) 5 years after initial ASMR "
                "rating when new evidence becomes available. Post-marketing studies (études post-inscription, "
                "EPI) may be requested by HAS to generate real-world comparative data that could support "
                "an improved ASMR rating in a later cycle."
            ),
        ],
    ),
    EvalSample(
        question="What are the key differences between full and conditional marketing authorisations granted by EMA?",
        ground_truth=(
            "A standard (full) marketing authorisation from EMA is granted when the complete clinical, "
            "non-clinical, and quality data are available and the benefit-risk balance is positive. A "
            "conditional marketing authorisation (CMA) is granted under exceptional circumstances when "
            "early clinical data are promising but comprehensive data are still pending, typically for "
            "serious or life-threatening conditions. CMA holders must fulfil specific post-marketing "
            "obligations (confirmatory data) within defined timelines. CMA is valid for one year and "
            "renewed annually. The EMA also grants authorisation under exceptional circumstances for "
            "diseases where comprehensive data cannot be generated."
        ),
        contexts=[
            (
                "EMA Regulation (EC 726/2004) provides the legal basis for centralised marketing "
                "authorisations. Standard (full) MAs require complete clinical, non-clinical (Module 4), "
                "and quality (Module 3) data demonstrating efficacy, safety, and acceptable benefit-risk "
                "balance. Conditional MAs (CMA) under Regulation (EC) 507/2006 are granted when the "
                "benefit of immediate availability outweighs the risk of less comprehensive data — "
                "applicable in serious/life-threatening conditions with unmet medical need."
            ),
            (
                "CMA holders must fulfil specific obligations (SOBs) — additional post-marketing studies "
                "required within agreed timelines. CHMP reviews CMA annually to verify that the benefit-risk "
                "balance remains positive and obligations are on track. Successful completion converts CMA "
                "to a full standard MA. A CMA is valid for one year and must be renewed annually until "
                "converted to a standard marketing authorisation."
            ),
            (
                "EMA's authorisation under exceptional circumstances (AEC) applies when comprehensive clinical "
                "data cannot be obtained due to the rarity of the condition or ethical constraints. AEC "
                "does not convert to a standard MA and requires annual review indefinitely. Both CMA and "
                "AEC include risk management plans (RMPs) and pharmacovigilance requirements."
            ),
        ],
    ),
    EvalSample(
        question="What phase of clinical trials do G-BA typically require for AMNOG submission?",
        ground_truth=(
            "G-BA requires phase III randomised controlled trial data as the primary evidence base for "
            "AMNOG benefit assessments. Phase II data alone are generally insufficient to establish "
            "added benefit. However, for oncology drugs receiving accelerated EMA approval based on phase "
            "II data (e.g. ORR from single-arm trials), G-BA typically rates benefit as 'Anhaltspunkt' "
            "(indication of added benefit, the lowest positive category) or 'Nicht belegt' (not proven). "
            "For rare diseases, phase II with robust effect sizes may be considered if phase III is "
            "infeasible. G-BA's strict evidence hierarchy significantly impacts drugs with early approvals."
        ),
        contexts=[
            (
                "G-BA's AMNOG process requires manufacturers to provide the highest quality evidence "
                "in their dossier, following a hierarchy: randomised controlled trials > observational "
                "studies > case series. Phase III RCTs comparing to the ZVT are vastly preferred. "
                "Phase I/II data are rarely sufficient to demonstrate any level of added benefit "
                "unless the effect size is extraordinary and the evidence certainty is high."
            ),
            (
                "In oncology, several drugs received EMA approval based on phase II single-arm trial "
                "data showing high ORR in treatment-refractory populations. In subsequent AMNOG assessments, "
                "G-BA classified these products as 'Anhaltspunkt für einen nicht quantifizierbaren "
                "Zusatznutzen' (indication of non-quantifiable added benefit) due to the absence of "
                "comparative trials against ZVT."
            ),
            (
                "G-BA's benefit assessment resolution specifies that lower levels of evidence result in "
                "lower benefit categories: proof (Beleg, highest) > indication (Anhaltspunkt) > hint "
                "(Hinweis). The level of evidence directly maps to the benefit category assigned and "
                "ultimately affects the reimbursement amount negotiated."
            ),
            (
                "For rare diseases where conducting a phase III trial is infeasible due to small patient "
                "populations or ethical constraints, G-BA may consider phase II data with robust effect "
                "sizes. In such cases, the benefit category is typically lower (Anhaltspunkt or Hinweis) "
                "reflecting the lower evidence certainty, but reimbursement is still possible."
            ),
        ],
    ),
    EvalSample(
        question="How does the CBG in the Netherlands evaluate biosimilar interchangeability?",
        ground_truth=(
            "The College ter Beoordeling van Geneesmiddelen (CBG) follows EMA guidance on biosimilars. "
            "In the Netherlands, biosimilar interchangeability (the ability to switch between reference "
            "biologic and biosimilar or between biosimilars) is assessed at the prescriber level — "
            "automatic substitution at pharmacy without prescriber consent is generally not permitted. "
            "Zorginstituut Nederland (ZIN, the Dutch HTA body) evaluates cost-effectiveness for reimbursement "
            "decisions. The Netherlands uses a tender system (preferentiebeleid) for biosimilars in the "
            "community pharmacy setting, where the lowest-cost product is automatically dispensed unless "
            "the prescriber specifies otherwise."
        ),
        contexts=[
            (
                "In the Netherlands, the CBG (College ter Beoordeling van Geneesmiddelen — Medicines "
                "Evaluation Board) follows EMA guidance on biosimilars and is responsible for national "
                "marketing authorisations. EMA's centralised approval is recognised, and CBG does not "
                "conduct separate clinical evaluations. Biosimilar interchangeability — the ability to "
                "switch between the reference biologic and a biosimilar or between biosimilars — is "
                "assessed at the prescriber level; automatic substitution at pharmacy without prescriber "
                "consent is generally not permitted in the Netherlands."
            ),
            (
                "Zorginstituut Nederland (ZIN) conducts HTA for reimbursement decisions. For biosimilars, "
                "ZIN generally does not conduct a full HTA as clinical effectiveness follows the reference "
                "product. Instead, decisions focus on price and budget impact. The preferentiebeleid "
                "(preference policy) in community pharmacy mandates dispensing of the lowest-priced product "
                "in a therapeutic group unless medically contra-indicated."
            ),
            (
                "Dutch hospital procurement uses centralized tender processes where biosimilars compete "
                "against original biologics. Winning products receive exclusive supply contracts for "
                "hospital pharmacies for 1–3 years. Price reductions of 30–60% below originator list "
                "price have been achieved for infliximab, rituximab, and trastuzumab biosimilars in "
                "Dutch tenders."
            ),
        ],
    ),
    EvalSample(
        question="What are the managed entry agreements commonly used for high-cost oncology drugs in Europe?",
        ground_truth=(
            "Managed entry agreements (MEAs) for oncology drugs in Europe include: (1) financial-based "
            "agreements: price-volume agreements, expenditure caps, confidential discounts; (2) "
            "outcomes-based agreements: payment-by-results, conditional treatment continuation, "
            "coverage with evidence development. Italy uses AIFA registries extensively for MEAs. "
            "Germany uses cost-sharing for drugs rated as 'no added benefit'. The UK NHS negotiates "
            "commercial access agreements with NICE appraisal support. Patient Access Schemes (PAS) "
            "in England and Wales offer confidential rebates. MEAs are particularly prevalent for "
            "ATMPs and CAR-T therapies where long-term durability is uncertain."
        ),
        contexts=[
            (
                "Managed entry agreements (MEAs) bridge the gap between manufacturer pricing and payer "
                "willingness-to-pay under uncertainty. Financial MEAs include: simple price discounts, "
                "price-volume agreements (price decreases as volume increases), cap on annual expenditure, "
                "and free-of-charge access for initial treatment cycles. These do not require post-marketing "
                "outcome data collection."
            ),
            (
                "Outcomes-based MEAs (also called performance-based risk-sharing arrangements, PBRSAs) "
                "link payment to clinical outcomes observed in real-world use. Examples: AIFA payment-by-results "
                "for oncology drugs via registri AIFA; NHS England outcome-based arrangements for gene therapies; "
                "conditional treatment continuation where continued reimbursement requires response by cycle 3. "
                "Italy and the UK have the most developed frameworks for PBRSAs in Europe."
            ),
            (
                "Patient Access Schemes (PAS) in England: manufacturers propose a PAS to NICE at the time "
                "of appraisal. NICE's Patient Access Scheme Liaison Unit (PASLU) assesses complexity. "
                "Simple PAS (fixed percentage discount) are preferred; complex PAS (response-based rebates) "
                "are accepted with caution due to administrative burden. Net prices are commercially "
                "confidential to prevent international reference pricing impact."
            ),
            (
                "In Germany, drugs receiving a 'kein Zusatznutzen belegt' (no added benefit proven) AMNOG "
                "rating are subject to cost-sharing: the GKV-Spitzenverband negotiates a reimbursement "
                "amount benchmarked to the cost of the appropriate comparator. The UK NHS negotiates "
                "commercial access agreements with NICE appraisal support for high-cost medicines, "
                "including within the Cancer Drugs Fund (CDF) pathway. MEAs are particularly prevalent "
                "for ATMPs and CAR-T therapies where long-term durability data are still maturing."
            ),
        ],
    ),
    EvalSample(
        question="What is the process for orphan drug designation in the EU and what incentives does it provide?",
        ground_truth=(
            "EU orphan drug designation (ODD) is granted by EMA (Committee for Orphan Medicinal Products, "
            "COMP) for conditions affecting fewer than 5 in 10,000 EU citizens or where profitability is "
            "insufficient without incentives. Benefits include: 10-year market exclusivity upon approval "
            "(preventing competing products), fee reductions for EMA regulatory procedures, access to "
            "COMP scientific advice and protocol assistance, and eligibility for EU grant funding. "
            "The ODD is product-specific, not company-specific. Market exclusivity can be revoked if "
            "the drug is sufficiently profitable or if a similar drug with greater benefit is approved."
        ),
        contexts=[
            (
                "EU Regulation (EC) No 141/2000 on orphan medicinal products established the EU orphan "
                "drug framework. Applications for orphan designation are submitted to EMA at any point "
                "before marketing authorisation. COMP evaluates: prevalence criterion (< 5 in 10,000), "
                "medical plausibility of the condition, and medical plausibility of the drug's benefit. "
                "The ODD is product-specific, not company-specific — if product ownership transfers, "
                "the designation transfers with it. A drug can hold multiple ODDs for different conditions."
            ),
            (
                "Incentives of EU orphan designation: 10-year market exclusivity following central MA "
                "(extended to 12 years for paediatric ODD with PIP compliance), fee reductions/waivers "
                "for EMA scientific advice and application fees, access to administrative support, protocol "
                "assistance, eligibility for Horizon Europe research funding."
            ),
            (
                "Market exclusivity for orphan drugs prevents EMA from granting a marketing authorisation "
                "for a similar medicine for the same condition unless the competitor demonstrates clinical "
                "superiority (greater efficacy, fewer side effects, greater safety) or if the orphan "
                "medicine holder has lost designation status or cannot supply sufficient quantities. "
                "Market exclusivity may also be revoked if post-approval data show the drug is "
                "sufficiently profitable without the incentive."
            ),
        ],
    ),
    EvalSample(
        question="What are the requirements for health economic models submitted to NICE technology appraisals?",
        ground_truth=(
            "NICE requires health economic models for technology appraisals to follow the reference case "
            "as defined in the NICE Manual for Guidance Development. Key requirements: the perspective is "
            "the NHS and personal social services; time horizon must be sufficient to capture all relevant "
            "differences in costs and outcomes (often lifetime); the preferred outcome measure is QALY "
            "using EQ-5D utility values from the UK population; discounting at 3.5% per year for both costs "
            "and outcomes; costs in GBP at the retail price or NHS-negotiated price. Models are typically "
            "Markov state-transition models or individual patient simulation. The Evidence Review Group "
            "(ERG) critically appraises and often reruns the manufacturer's model."
        ),
        contexts=[
            (
                "NICE technology appraisal reference case requirements (NICE Manual 2022): (1) perspective — "
                "direct NHS and PSS costs; (2) time horizon — long enough to capture all relevant cost and "
                "health differences, typically lifetime for chronic conditions; (3) health outcomes — "
                "QALYs calculated using preference-based HRQoL instruments, preferably EQ-5D; (4) discount "
                "rate — 3.5% per annum for both costs and health outcomes; (5) costs expressed in GBP at "
                "the retail price or NHS-negotiated price; (6) comparing against the most plausible "
                "cost-effective alternative."
            ),
            (
                "Model structure for NICE submissions: Markov cohort models are standard for many oncology "
                "and chronic disease appraisals. Partitioned survival models (PartSA) are common in oncology "
                "using survival data from RCTs with extrapolation. Individual patient simulation (IPS) may "
                "be used when patient heterogeneity is important. All models must be submitted as executable "
                "files (typically Excel with VBA or R) for the Evidence Review Group (ERG) to critically "
                "appraise; the ERG often reruns the manufacturer's model to validate assumptions and test "
                "alternative scenarios."
            ),
            (
                "Uncertainty handling in NICE models: deterministic sensitivity analysis (one-way), "
                "probabilistic sensitivity analysis (PSA) using Monte Carlo simulation with 10,000+ "
                "iterations, scenario analyses for structural assumptions (e.g. different extrapolation "
                "models for survival data). Cost-effectiveness acceptability curves (CEACs) are reported "
                "to show probability of cost-effectiveness at different WTP thresholds."
            ),
        ],
    ),
    EvalSample(
        question="How has EMA's adaptive pathway approach changed the approval landscape for medicines?",
        ground_truth=(
            "EMA's adaptive pathways (formerly called adaptive licensing) is a prospective, iterative "
            "approach to medicine approval. Drugs enter the market in a restricted population where "
            "benefit-risk is clearest, then expand with accumulating evidence. This approach was piloted "
            "from 2014–2016 and influenced EMA's pragmatic clinical evidence framework. Key features: "
            "early interaction between developers and regulators (and HTA bodies), iterative approval "
            "scopes, use of real-world evidence for confirmatory data, and close links with conditional "
            "MA. The EMA-EUnetHTA parallel scientific advice supports joint regulatory-HTA engagement "
            "from early development."
        ),
        contexts=[
            (
                "EMA's Adaptive Pathways (formerly adaptive licensing) pilot ran from 2014–2016 with 30 "
                "product concepts evaluated. The concept allows initial approval in a restricted patient "
                "population (early market entry) followed by iterative label expansion as real-world and "
                "confirmatory data emerge. This aligns with the 'learn and confirm' paradigm rather than "
                "waiting for full RCT datasets before any patient access."
            ),
            (
                "EMA-HTA parallel scientific advice was formalized post-pilot. Manufacturers can request "
                "simultaneous scientific advice from EMA and participating HTA bodies (typically via "
                "EUnetHTA joint SAs). This ensures clinical development plans generate data that satisfy "
                "both regulatory and HTA evidence requirements — reducing post-approval evidence gaps."
            ),
            (
                "Adaptive pathways are particularly relevant for: ATMPs and gene therapies (long-term "
                "evidence collection via registries), oncology drugs with initial approval in "
                "treatment-refractory patients expanding to earlier lines, and rare diseases where "
                "phase III trials are ethically or practically infeasible. Real-world evidence (RWE) "
                "from electronic health records and registries supports iterative evidence generation."
            ),
            (
                "The adaptive pathways pilot influenced EMA's broader pragmatic clinical evidence framework, "
                "encouraging iterative evidence generation and early regulatory-developer dialogue. Adaptive "
                "pathways have close operational links with conditional marketing authorisation (CMA): "
                "initial restricted approvals are often granted as CMAs, with real-world evidence and "
                "post-market studies fulfilling specific obligations that support subsequent label expansion "
                "or conversion to full marketing authorisation. The EMA-EUnetHTA parallel scientific advice "
                "supports joint regulatory-HTA engagement from early development."
            ),
        ],
    ),
]
