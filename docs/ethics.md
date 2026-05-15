# Ethics and Responsibility

## Core Principles

### 1. Respect for Indigenous and Minority Languages

Place names in minority and indigenous languages (Sámi, Basque, Sorbian, Romani, Cornish, Welsh, Breton, Catalan, etc.) represent living cultural heritage. This project:

- Treats all language layers as equally valid data
- Never privileges a majority-language form as "correct"
- Consults with relevant communities before publishing analyses of sensitive sites
- Documents colonial and assimilation history explicitly

### 2. Acknowledging Historical Violence

Many European place name landscapes bear traces of forced renaming:
- **Norwegianization** (fornorskning) of Sámi and Kven names
- **Russification** of Finnish, Baltic, and Ukrainian names
- **Germanization** of Slavic names in Eastern Europe
- **Anglicization** of Welsh, Scottish Gaelic, and Irish names
- **Hellenization** of Slavic and Turkish names in Greece
- **Turkification** of Armenian, Greek, and Kurdish names

These processes are documented as data (renaming events with actors and motivations), never hidden or normalized.

### 3. Disputed Territories

For contested areas (Northern Ireland, Cyprus, Crimea, Western Sahara, etc.):
- All attested name forms are recorded without privileging one
- No automatic preference for the controlling state's official form
- Temporal and political context is explicit
- The project does not take political positions

### 4. Sacred and Sensitive Sites

Some place names refer to indigenous sacred sites, burial grounds, or ceremonially restricted locations:
- Such information is only included with community consent
- Precise locations may be generalized when requested
- Cultural protocols are respected

## Data Governance

### Provenance
- Every record carries its source, access date, and license
- Interpretations carry author, date, and confidence
- Automated analyses are clearly distinguished from expert opinions

### Privacy
- No personal data about living individuals
- Historical personal names in place names are treated as historical data
- Contributor identities are protected per standard open-source practice

### GDPR and Historical Person-Names

Place names frequently derive from personal names (anthroponymic toponyms). The framework handles these under the following GDPR-compliant policy:

#### Applicability

GDPR (Regulation (EU) 2016/679) applies to data relating to **identified or identifiable living natural persons** (Art. 4(1)). It does **not** apply to:
- Deceased persons (Recital 27: "This Regulation does not apply to the data of deceased persons")
- Names that have become geographic designators regardless of their personal origin
- Statistical analyses of name-element distributions (fully anonymized)

#### Jurisdiction-Specific Thresholds

National implementations vary on when person-derived data becomes "historical" and exempt from privacy restrictions:

| Country/Region | Threshold | Legal Basis | Notes |
|---|---|---|---|
| **Norway** | 10 years after death OR >100 years since birth | Personopplysningsloven §2, Archives Act | Shorter for public figures; church/census records public after 60/100 years |
| **Sweden** | No explicit post-mortem GDPR; 70-year secrecy for census | GDPR + Offentlighets- och sekretesslagen | Person data in research exempt under ethical review |
| **Denmark** | 10 years after death; census open after 75 years | Databeskyttelsesloven §2(5) | Church books open after 50 years |
| **Finland** | GDPR ceases at death; archive records open 25-50 years | Tietosuojalaki §2 | Depends on sensitivity of content |
| **Iceland** | GDPR ceases at death | Lög um persónuvernd §4 | Small population → extra care for identifiability |
| **UK** | GDPR ceases at death; living persons only | UK GDPR Art. 4(1) | Common law privacy may extend to recently deceased |
| **Germany** | 10 years post-mortem (Postmortaler Persönlichkeitsschutz) | BGB §1922 + BDSG | Dignity protection extends beyond death |
| **France** | GDPR ceases at death | CNIL guidance 2020 | Loi Informatique et Libertés applies to living only |
| **EU General** | GDPR does not apply to deceased (Recital 27) | Member states may extend | Always check national implementation |

#### Project Policy

1. **Place names derived from persons dead >100 years**: Freely usable as historical-linguistic data. No GDPR concern. This covers >99% of toponymic material (medieval farm owners, Viking-age settlers, saints, kings).

2. **Place names derived from persons dead 10–100 years**: Usable as geographic/linguistic data. The place name itself is not personal data—it is a geographic designator. The *etymology* may reference the person, which is permissible under:
   - GDPR Recital 27 (not applicable to deceased)
   - National archive law (records public after threshold)
   - Research exemption (Art. 89(1))

3. **Place names referencing living persons**: Rare in traditional toponymy. When encountered (e.g., streets named after living politicians):
   - Record only the geographic name, not biographical data
   - Do not store personal details beyond what is publicly available in official gazetteers
   - No profiling, no special category data processing

4. **Contributor data**: Protected under standard open-source practice. Git commit metadata (name, email) is voluntary and public by choice.

#### Practical Implementation

- The `source_reliability` field never contains personal identifying information
- Interpretation records store scholarly attribution (published author names = public)
- Ethnonym distributions (*Finn-*, *Kvæn-*) are aggregated statistical patterns, not personal data
- Search/query logs are not retained beyond the session

#### Research Exemption (Art. 89)

When processing historical records that *might* reference identifiable persons (e.g., 19th-century census data linking farmers to farms), the project relies on GDPR Art. 89(1) research exemption with appropriate safeguards:
- Purpose limitation (toponymic research only)
- Data minimization (only name and location, no other personal details)
- No individual-level output (only statistical patterns)

#### Review Trigger

This policy shall be reviewed if:
- A national DPA issues guidance specifically about toponymic research
- The project begins processing records from the last 100 years at scale
- A data subject or descendant raises a concern

### Licensing
- Aggregated outputs respect the most restrictive input license
- Each record's license is tracked individually
- Users are warned when combining datasets with incompatible licenses

## Responsible Publication

### Uncertainty Communication
- All results include confidence intervals and effect sizes
- P-values are never reported without context
- Conclusions are explicitly qualified by robustness results

### Avoiding Misuse
- Analyses of ethnic/linguistic distributions are not suitable for political instrumentalization
- The project explicitly disclaims support for ethno-nationalist readings
- Findings about historical populations do not imply territorial claims

## Community Engagement

- Indigenous language communities are invited as collaborators, not subjects
- Local expertise is valued alongside computational methods
- The project supports language revitalization efforts where relevant
- Feedback mechanisms allow communities to flag concerns
