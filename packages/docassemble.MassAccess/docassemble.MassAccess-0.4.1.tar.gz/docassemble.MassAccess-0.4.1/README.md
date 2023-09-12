# docassemble.MassAccess

Branding for the CourtFormsOnline.org website; implementation of 
https://github.com/suffolklitlab/docassemble-AssemblyLine

## Favicons

This packages contains three sets of favicons for three servers we use: 
one for production, one for testing, and one for development. They were generated using https://realfavicongenerator.net.

To use these favicons on your docassemble server, add the following to your Configuration:
```yaml
favicon: docassemble.MassAccess:data/static/favicon
favicon mask color: "#002e5d"
favicon theme color: "#ffffff"
```

To use the developer or test favicons, change the first line to point to those directories:
```yaml
favicon: docassemble.MassAccess:data/static/test_favicon
```
