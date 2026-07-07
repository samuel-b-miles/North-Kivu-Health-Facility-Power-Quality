# DHIS2 Anonymization Protocol

Raw DHIS2 exports and the private facility crosswalk are excluded from Git.
Public panels omit raw facility names, DHIS2 organisation-unit identifiers,
organisation-unit codes, district identifiers, and free-text fields.

The private crosswalk lives at
`config/private/facility_crosswalk_private.csv`. It maps raw DHIS2 entities to
stable public IDs and is required only when rebuilding public panels from
authorized raw exports. The public files can be analysed without that key.

The two similarly named raw control entities are never merged. The designated
reference facility is mapped to `FAC_C03`; the alternate medical-centre entity
is excluded and recorded in the local, Git-ignored QA mapping audit.
