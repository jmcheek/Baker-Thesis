# Full CSV pipeline results

**191 bills have full statute text files; 1 remains unresolved.**

HTML extraction added 60 files. All 85 existing files retained identical SHA-256 hashes. All 191 files have metadata, legislative history and statutory-text sections.

The initial HTML run extracted all 62 previously unresolved HTML sources and assembled 60; subsequent reviewed imports resolved the two missing act-number filenames. HTML layout and CSS redlining require visual review.

HTML self-tests passed. Offline run: no API requests.

| Remaining reason | Count |
| --- | ---: |
| Offline cache miss: sessions_PR | 1 |

[Detailed report](20261001T144935022Z_36796.json).

[Retrieved bills](../retrieved.csv) and [unresolved bills](../unresolved.csv).

Colorado SB4 was subsequently resolved using the user-supplied enrolled-text link for the 2025 first special session. The targeted API run saved metadata, all 15 history actions, the original seven-page PDF, and extracted text. Title and enactment date agree with NCSL. Offline rerun preserved the statute. Enrolled-text and visual-review notes remain. [Targeted run report](20261001T183350346Z_23616.json).

Delaware HB16 (Volume 85, Chapter 17) was subsequently retrieved after comparing LegiScan document 3088562, labelled Draft, against the official session-law PDF. Sections 1 and 2 match after whitespace and page-footer normalization. The API label and HTML redlining review note are preserved. Seven history actions, refreshed API responses, source HTML and the official PDF are retained. Offline rerun preserved the statute. [Targeted run report](20261001T184803901Z_4764.json).

Delaware HB105 (Volume 85, Chapter 228) was resolved to House Substitute 2, LegiScan document 3252331. Sections 1 and 2 match the official session-law PDF after whitespace and page-footer normalization. Earlier drafts are excluded and the API Draft label remains. Current API metadata and history, API text response, source HTML, official PDF and extracted texts are saved. [Targeted run report](20261001T190234046Z_40720.json).

Florida HB757 (Chapter 2025-99) was resolved to LegiScan H0757 using the supplied link and official Florida Senate identity record. API metadata, all history actions, enrolled PDF and extracted text are saved. NCSL May 27 approval and LegiScan May 28 chaptering dates are both retained; official-act and visual comparison notes remain. [Targeted run report](20261001T191323386Z_52180.json).

Florida HB907 (Chapter 2025-187) was resolved to LegiScan H0907 using the official Florida Senate record. API metadata and history, enrolled PDF and extracted text are saved. NCSL June 25 approval and LegiScan June 26 chaptering dates are both retained; standard visual and official-act comparison notes remain. [Targeted run report](20261009T000644965Z_18044.json).

Florida HB1103 (Chapter 2025-130) was resolved to LegiScan H1103. API metadata and history, enrolled PDF and extracted text are saved. Both source titles and June 9 approval / June 10 chaptering dates are retained; standard review notes remain. [Targeted run report](20261009T001016986Z_42236.json).

Florida SB2500 (Chapter 2025-198) was resolved to LegiScan S2500. API metadata and history, enrolled HTML and extracted text are saved. June 30 approval and July 2 chaptering dates are retained. Enrolled text is explicitly flagged for line-item veto comparison against the final chapter law. [Targeted run report](20261009T001314302Z_37108.json).

Hawaii HB718 (Act 86; NCSL filename act 2025-86) was resolved to final CD1, API document 3222577 labelled Amended. Sections 1-3 compared against signed Act 86 in Governor Message 1186; two PDF extraction artifacts were visually checked on statutory page 3. API metadata/history, HTML, signed-act PDF and extracted texts are retained. HTML review notes remain. [Targeted run report](20261009T001541716Z_29728.json).

Hawaii SB742 (Act 154) was resolved to final CD1, API document 3222568 labelled Amended. Statutory provisions compared with signed Act 154 in Governor Message 1254; two OCR capitalization differences visually confirmed on statutory page 2. API metadata/history, HTML, signed-act PDF and extracted texts are retained. HTML review notes remain. [Targeted run report](20261009T001851938Z_72856.json).

Iowa SF647 (NCSL SB647, Act 157) was retrieved using the verified bill-number mapping. API metadata and history, enrolled HTML and extracted text are saved. Governor item vetoes are explicitly flagged for final chapter-law comparison. [Targeted run report](20261009T002046886Z_43120.json).

Louisiana HB1 (Act 1) was resolved to the 2025 regular-session appropriations bill, excluding the special-session namesake. API metadata/history, chaptered PDF and extracted text are saved. NCSL and API enactment dates agree. Standard review notes remain. [Targeted run report](20261009T002138441Z_28440.json).

Maine deed-fraud entry SB139 was resolved to S.P. 139 / L.D. 353, Resolve Chapter 104. Official chaptered text confirms July 1 approval; API June 25 status records final passage. API metadata/history, chaptered PDF and extracted text are saved; original NCSL candidate/filename retained. [Targeted run report](20261009T002508546Z_62504.json).

Maine consumer-transparency entry HB1154 was resolved to H.P. 1154 / L.D. 1727, Public Law Chapter 294. Official chaptered text confirms June 12 approval; API June 10 status records legislative enactment vote. API metadata/history, chaptered PDF and extracted text are saved; original NCSL candidate/filename retained. [Targeted run report](20261009T002756125Z_20916.json).

Maine private-images entry HB1303 was resolved to H.P. 1303 / L.D. 1944, Public Law Chapter 400. StateNet link was inaccessible; official legislature chaptered PDF used. June 20 approval and API June 16 legislative enactment vote retained separately. API metadata/history, chaptered PDF and extracted text saved. [Targeted run report](20261009T002912917Z_66432.json).

Minnesota HF2432 (NCSL HB2432, Chapter 35) was retrieved using current LegiScan metadata/history and the official Revisor chapter PDF. StateNet was inaccessible and API text versions were earlier engrossments. Official source is recorded in the resolution and run report, with no invented API document ID. Date and chapter identity agree; visual review remains. [Targeted run report](20261009T003225233Z_63464.json).

Mississippi SB2426 was assembled from cached API metadata/history and enrolled HTML after official status XML confirmed March 18 approval. Act number is unavailable; reviewed filename MS_SB2426_Signed-2025-03-18.txt is used with explicit metadata note. HTML and official-act review notes remain. [Targeted run report](20261009T003526262Z_64924.json).

Montana HB82 (Act 102) was assembled using the latest enrolled document linked by LegiScan, 3247059, resolving two equally ranked enrolled texts. Explicit document selection saved for reruns. API metadata/history, enrolled PDF and extracted text retained; standard review notes remain. [Targeted run report](20261009T003818635Z_36588.json).

Nebraska LB77 was assembled from cached API metadata/history and chaptered slip-law PDF, confirming June 4 approval. Act number unavailable; reviewed filename NE_LB77_Signed-2025-06-04.txt used. API June 6 status date retained separately. [Targeted run report](20261009T003953955Z_57828.json).

Nebraska LB371 was assembled from cached API metadata/history and chaptered slip-law PDF, confirming May 30 approval. Act number unavailable; reviewed filename NE_LB371_Signed-2025-05-30.txt used. API June 2 history date retained separately. [Targeted run report](20261009T004033213Z_51576.json).

Nebraska LB383 was assembled from cached API metadata/history and chaptered slip-law PDF, confirming May 20 approval. Act number unavailable; reviewed filename NE_LB383_Signed-2025-05-20.txt used. API May 21 history date retained separately. [Targeted run report](20261009T004121233Z_62508.json).

New Hampshire HB143 (Chapter 270) assembled using official final chapter PDF and cached API metadata/history. Supplied introduced text differs substantially from final law and was excluded. Official August 1 approval and API August 11 status dates retained separately. [Targeted run report](20261009T004251983Z_54008.json).

Nebraska LB504 was assembled from cached API metadata/history and chaptered slip-law PDF, confirming May 30 approval. Act number unavailable; reviewed filename NE_LB504_Signed-2025-05-30.txt used. API June 2 status retained separately. [Targeted run report](20261009T004332868Z_73476.json).

New Hampshire SB300 (Chapter 259) assembled using official final chapter PDF and cached API metadata/history; introduced version excluded. Official July 15 approval and API July 22 status dates retained separately. [Targeted run report](20261009T004520964Z_3708.json).

New Jersey A3540 (NCSL AB3540, P.L.2025 Chapter 40) resolved to the 2024-2025 session and stored under 2025 enactment year. API metadata/history, chaptered HTML and extracted text saved. Dates agree; HTML review notes remain. [Targeted run report](20261009T004631484Z_34768.json).

New York S822 (NCSL SB822, Chapter 96) resolved by bill-number mapping. Official Senate history shows unamended bill signed February 14; statutory words of API Introduced text match official Senate PDF after layout/redlining-marker normalization. API label and HTML review notes retained. Current metadata/history, source HTML and official Senate PDF saved. [Targeted run report](20261009T004906078Z_45808.json).

New York A2249 (NCSL AB2249, Chapter 66) resolved by bill-number mapping. Official Senate history shows unamended bill signed February 14; API text matches official Senate PDF after layout/redlining-marker normalization. API Introduced label and HTML review notes retained. API metadata/history, source HTML and official PDF saved. [Targeted run report](20261009T005031303Z_19508.json).

New York A3000D (NCSL AB3000, Chapter 50) resolved to adopted D version. API amended text matches official Senate PDF after layout/redlining-marker normalization. Earlier versions excluded. API metadata/history, HTML and official PDF saved; API label, HTML and final chapter/veto review notes retained. [Targeted run report](20261009T005307138Z_66880.json).

New York S3006C (NCSL SB3006, Chapter 56) resolved to adopted C version. API amended text matches official Senate PDF after layout/redlining-marker normalization. Earlier versions excluded. API metadata/history, HTML and official PDF saved; API label, HTML and official chapter review notes retained. [Targeted run report](20261009T005558372Z_30092.json).

New York S3008C (NCSL SB3008, Chapter 58) resolved to adopted C version. API text matches official Senate PDF after layout/redlining-marker normalization. API metadata/history, HTML and official PDF saved; API Amended label and official chapter/HTML review notes retained. [Targeted run report](20261009T005735084Z_52804.json).

New York S7882 (NCSL SB7882, Chapter 437) resolved by bill-number mapping. Official Senate history shows unamended bill signed October 16, 2025; API text matches official Senate PDF after layout normalization. API Introduced label and HTML review notes retained. Metadata/history, source HTML and official PDF saved. [Targeted run report](20261009T005936652Z_57476.json).

North Carolina H125 (NCSL HB125, Session Law 2025-89) resolved by bill-number mapping. API metadata/history, chaptered PDF and extracted text saved. Enactment dates agree. [Targeted run report](20261009T010131688Z_67580.json).

North Carolina H805 (NCSL HB805, Session Law 2025-84) resolved by bill-number mapping. API metadata/history, including veto override, chaptered PDF and extracted text saved. Enactment dates agree. [Targeted run report](20261009T010323416Z_61820.json).

Pennsylvania SB649 assembled from official enacted Act 35 PDF and cached API metadata/history. NCSL omitted the act number; reviewed official source supplies Act 35 explicitly in metadata. Earlier API text excluded. [Targeted run report](20261009T010520045Z_34804.json).

Rhode Island S0136 (NCSL SB136, Chapter 2025-429) assembled using official public-law HTML and current API metadata/history. Introduced API text excluded. Identity/date agree; HTML review notes retained. [Targeted run report](20261009T010727367Z_68676.json).

Rhode Island S1039 Substitute A (NCSL SB1039, Chapter 2025-140) assembled using official public-law HTML and current API metadata/history. API committee-substitute text excluded. Identity/date agree; HTML review notes retained. [Targeted run report](20261009T010850870Z_66328.json).

Rhode Island S0816 Substitute A (NCSL SB816, Chapter 2025-410) assembled using official public-law HTML and current API metadata/history. Identity/date agree; HTML review notes retained. [Targeted run report](20261009T011016998Z_35664.json).

Rhode Island H5046 (NCSL HB5046, Chapter 2025-430) assembled using official public-law HTML and current API metadata/history. Identity/date agree; HTML review notes retained. [Targeted run report](20261009T011127472Z_57224.json).

Rhode Island H5872 Substitute A (NCSL HB5872, Chapter 2025-409) assembled using official public-law HTML and current API metadata/history. Identity/date agree; HTML review notes retained. [Targeted run report](20261009T011348569Z_32752.json).

Rhode Island H5985 Substitute A (NCSL HB5985, Chapter 2025-139) assembled using official public-law HTML and current API metadata/history. Identity/date agree; HTML review notes retained. [Targeted run report](20261009T011510959Z_58940.json).

South Carolina S0028 (NCSL SB28, Act 57) assembled using official enacted-act HTML and current API metadata/history. Official May 22 approval and API May 27 act-number status retained separately; HTML review notes remain. [Targeted run report](20261009T011614158Z_66180.json).

South Carolina S0029 (NCSL SB29, Act 58) identified through user roll-call link and assembled using official enacted-act HTML and current API metadata/history. Official May 22 approval and API May 27 act-number status retained separately; HTML review notes remain. [Targeted run report](20261009T011709604Z_60460.json).

South Carolina H3058 (NCSL HB3058, Act 37) assembled using official enacted-act HTML and current API metadata/history. Official May 12 approval and API May 19 act-number status retained separately; HTML review notes remain. [Targeted run report](20261009T011801254Z_39544.json).

Texas HB149 (Act 1174) resolved to the 89th regular session, excluding distinct special-session bills with the same number. API metadata/history and full enrolled HTML saved. June 22 signature date agrees with NCSL and official legislature history; enrolled/HTML review notes remain. [Targeted run report](20261009T012009642Z_32216.json).

Virginia SB731, Chapter 262, resolved to the 2024 regular session using the supplied StateNet identifier, original NCSL March 28, 2024 date, and official chapter. API metadata/history and chaptered HTML saved. Original 2025 dataset grouping retained with explicit discrepancy note; HTML review remains. [Targeted run report](20261009T012343233Z_32200.json).

Virginia HB1083, Chapter 410, resolved to the 2024 regular session using the supplied StateNet identifier and original NCSL April 4, 2024 date. API metadata/history and chaptered HTML saved. Original 2025 dataset grouping retained with explicit discrepancy note; HTML review remains. [Targeted run report](20261009T012650274Z_47388.json).

Texas HCR53 congratulatory resolution assembled from refreshed API metadata/history and enrolled HTML. Official legislature history confirms April 9, 2025 signature. No act number supplied; reviewed signature-date filename used. Enrolled and HTML review notes remain. [Targeted run report](20261009T012811855Z_3184.json).

Latest full offline verification preserved all 191 assembled files; Puerto Rico HJR68 remains unresolved (missing session cache). All 191 SHA-256 hashes were unchanged and HTML extraction self-tests passed. [Full verification report](20261009T013249717Z_15468.json).
