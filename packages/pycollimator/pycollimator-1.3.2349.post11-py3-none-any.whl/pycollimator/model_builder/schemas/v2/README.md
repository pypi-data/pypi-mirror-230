# v2 schemas

An experimental approach to generating schemas and Go types from
TypeScript definitions.

## Define types

Since we use a mix of many different codegen tools (quicktype, oapi-codegen,
rtk-query-codegen, etc) we need to define types in a way that is compatible
with all of them. This is often tricky as they all have their own quirks.

1. Define types and interfaces in TypeScript files
1. First line should be `// SKIP` if the TS file should not be use for codegen
   (eg. it is imported by another file)
1. First line should be `// TYPE: TopLevelTypeName` if the JSON schema needs
   a top-level definition. This has weird implications but you could see
   oapi-codegen fail if the type is not top-level (see ModelOverrides, at the
   moment of writing this).

## Generate files

Run `generate.sh`.
This will generate json schemas, go types (from the json schemas) and copy the
TS files to the frontend.
