# Interview notes

Use these as discussion points grounded in the project, not claims of employer savings.

**Fuel and pricing:** Explain how dispatch experience helps identify routes where delays, stop density and equipment conditions change cost-to-serve. In this project you separated fuel from nonfuel costs, kept revenue fixed, and tested ±10% shocks. Demonstrate why a weighted margin is more useful than averaging percentages. Ask what empty-mile, fuel purchase and contract data would be needed to move from this demonstration to a carrier pricing decision.

**Ocean disruption:** Walk through the freight increase and extra days separately. Inventory carrying cost converts time into a financial exposure. Explain why a rerouting premium should be compared with avoided incremental carry and separately substantiated service penalties. Show that baseline carry is included once and margin erosion is in percentage points.

**Air cargo:** Show the 0% fuel-reduction case before the 20% assumed case. At zero savings, the nonfuel premium makes the A350F example more expensive; the default assumption reverses the ranking. Explain why a manufacturer claim does not supply mission fuel, net payload or fleet economics. Distinguish payload utilization from aircraft-hour utilization and a ceiling screen from flight planning.

**Vendor risk:** Discuss operational dependencies such as dispatch systems, carrier lane concentration and recovery alternatives. Demonstrate the incomplete vendor: leaving cybersecurity blank produces missing evidence, not low risk. Explain what evidence would support changing a score and how weights represent policy, not an empirical failure probability.

## Demonstration sequence

1. Filter Detroit–Cleveland in fuel; show base then +10%, explain contribution/load and target rate.
2. Change ocean extra days from 10 to 0 while leaving freight +25%; isolate inventory delay from freight inflation.
3. Change air reduction from 20% to 0%; show the ranking reversal. Raise distance above 8700 km to demonstrate withheld economics.
4. Open vendor risk, inspect missing cybersecurity, and enter a score only as a hypothetical. Restore the blank before presenting the original example.

Resume wording once you can explain and reproduce the work: “Built an independent Python/SQL logistics scenario project covering fuel-price exposure, freight-delay carrying costs, assumed air-cargo mission economics and evidence-based vendor review; prepared Power BI import tables and DAX measures.” Use “prepared” for Power BI until the report is built and verified there.
