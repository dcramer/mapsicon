import os
import shutil
import re
import json


def replace_unicode(s):
    # lazy
    return s.replace("å", "a").replace("ô", "o").replace("ç", "c").replace("é", "e")


def slugify(s):
    s = replace_unicode(s.lower().strip())
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s


# https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes
with open("all-countries.json", "rb") as fp:
    countries = json.load(fp)

outdir = "dist"

os.makedirs(outdir, 511, True)
os.makedirs(os.path.join(outdir, "assets"), 511, True)

folders = [x for x in os.listdir("all") if len(x) == 2]

import_statements = []
case_statements = []
for folder_name in folders:
    svg = os.path.join("all", folder_name, "vector.svg")

    # find country by alpha
    for country in countries:
        if country["alpha-2"].lower() == folder_name.lower():
            break
    else:
        raise Exception("Cant find country: " + folder_name)

    if country["alpha-2"] === "TW":
        country.update({
            "name": "Taiwan",
        })
    
    with open(svg) as fp:
        input_svg = fp.read()

    output_svg = input_svg.replace('fill="#000000"', 'fill="currentColor"')

    slug = slugify(country["name"])    
    if slug == "united-states-of-america":
        slug = "united-states"
    with open(os.path.join(outdir, "assets", slug + ".svg"), "w") as fp:
        fp.write(output_svg)

    norm_name = replace_unicode(re.sub(r"[\s\(\),'-\.]", "", country["name"]))
    import_statements.append('import %sMap from "./assets/%s.svg";' % (norm_name, slug))
    case_statements.append(
        """    case "%s":
       return <%sMap {...props} />;"""
        % (slug, norm_name)
    )

script = (
    """
import { type ComponentPropsWithoutRef } from "react";
      
%(import_statements)s

export default function CountryMapIcon({
  slug,
  ...props
}: ComponentPropsWithoutRef<"svg"> & { slug: string }) {
  switch (slug) {
%(case_statements)s
    default:
      return null;
  }
}
"""
    % {
        "import_statements": "\n".join(import_statements),
        "case_statements": "\n".join(case_statements),
    }
).strip()

with open(os.path.join(outdir, "index.tsx"), "w") as fp:
    fp.write(script)
