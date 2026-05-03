# The "4-hour battery" — why that duration became the industry default

When someone says "we need a BESS for this site", the default assumption is a **4-hour-duration lithium-ion** battery. There's a specific reason for that.

## Key numbers

* Standard duration: **4 hours** at nameplate discharge rate.
* Industry consensus: Li-ion LFP cells, round-trip efficiency ~92%, cycle life ~6,000 cycles at 80% depth of discharge.
* Per-MW CAPEX at 4-hour duration: **~$230–320/kWh installed** in 2024–2025 utility-scale projects.
* Augmentation practice: capacity fade of ~2.5%/yr is offset by replacing ~20% of cells at year 10.

## Where the "4 hours" number comes from

Three things, simultaneously:

1. **CAISO and ERCOT resource-adequacy accreditation.** Four-hour batteries receive ~100% capacity credit in both markets; two-hour batteries get ~60%. Shorter than 4h forfeits too much of the revenue stack.
2. **Evening-peak duration in most US TOU tariffs.** The "on-peak" window is typically 4 PM–9 PM (5 hours) in CA/TX/AZ. A 4-hour BESS can carry almost the full peak window if charged to 85% SOC by 4 PM.
3. **Fire code / energy density tradeoff.** 4-hour Li-ion sites fit ~2 MWh in a standard 20-ft container. Longer durations (6–8h) require either bigger footprint or different chemistry (flow batteries, iron-air).

## When not to use 4h

* Grid-services sites (frequency regulation, voltage support) often use 1–2h because they cycle many times per day and duration costs compound.
* Seasonal-shift sites (arbitraging winter-to-summer) use 8–12h flow batteries, not Li-ion.
* BTM DC sites: 4h is the right default. For this blog, BESS = 4h × DC IT nameplate.

## Sources

* CAISO Resource Adequacy Technical Bulletin 2024-01.
* NREL Annual Technology Baseline 2024, Storage chapter.
* Wood Mackenzie "US Energy Storage Monitor", 2024.
