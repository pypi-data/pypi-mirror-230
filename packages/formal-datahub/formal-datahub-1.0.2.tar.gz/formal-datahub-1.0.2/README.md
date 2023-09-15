# formal-datahub

This package allows you to sync your Formal Inventory with Datahub.

## Quickstart


Get familiar with Datahub Custom Sources and Actions:
    - https://datahubproject.io/docs/how/add-custom-ingestion-source
    - https://datahubproject.io/docs/actions



Install the Formal package:
`pip install formal-datahub`



See `/example` for examples. Be sure to set your secrets in environment variables.


---

# Examples

Run Ingestion: `datahub ingest -c ingest/formal_to_datahub.dhub.yaml`

Run Action: `datahub actions -c actions/datahub_to_formal.yaml`

If you are having trouble installing on M1, see the following: https://segmentfault.com/a/1190000040867082/en

