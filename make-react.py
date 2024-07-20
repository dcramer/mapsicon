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


COUNTRY_SCRIPT = """
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
""".strip()


def build_countries(outdir="dist/countryMapIcon"):
    # https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes
    with open("all-countries.json", "rb") as fp:
        countries = json.load(fp)

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

        if country["alpha-2"] == "TW":
            country.update(
                {
                    "name": "Taiwan",
                }
            )

        with open(svg) as fp:
            input_svg = fp.read()

        output_svg = input_svg.replace('fill="#000000"', 'fill="currentColor"')

        slug = slugify(country["name"])
        if slug == "united-states-of-america":
            slug = "united-states"
        with open(os.path.join(outdir, "assets", slug + ".svg"), "w") as fp:
            fp.write(output_svg)

        norm_name = replace_unicode(re.sub(r"[\s\(\),'-\.]", "", country["name"]))
        import_statements.append(
            'import %sMap from "./assets/%s.svg";' % (norm_name, slug)
        )
        case_statements.append(
            """    case "%s":\n      return <%sMap {...props} />;""" % (slug, norm_name)
        )

    script = COUNTRY_SCRIPT % {
        "import_statements": "\n".join(import_statements),
        "case_statements": "\n".join(case_statements),
    }

    with open(os.path.join(outdir, "index.tsx"), "w") as fp:
        fp.write(script)


STATE_SCRIPT = """
import { type ComponentPropsWithoutRef } from "react";

%(import_statements)s

export default function UsStateMapIcon({
  slug,
  ...props
}: ComponentPropsWithoutRef<"svg"> & { slug: string }) {
  switch (slug) {
    %(case_statements)s
    default:
      return null;
  }
}
""".strip()


def build_us_states(outdir="dist/usStateMapIcon"):
    os.makedirs(outdir, 511, True)
    os.makedirs(os.path.join(outdir, "assets"), 511, True)

    with open("us-states.json", "rb") as fp:
        states = json.load(fp)

    folders = [x for x in os.listdir("us") if len(x) == 2]

    import_statements = []
    case_statements = []
    for folder_name in folders:
        svg = os.path.join("us", folder_name, "vector.svg")

        try:
            name = states[folder_name.upper()]
        except KeyError:
            continue

        slug = slugify(name)

        with open(svg) as fp:
            input_svg = fp.read()

        output_svg = input_svg.replace('fill="#000000"', 'fill="currentColor"')

        with open(os.path.join(outdir, "assets", slug + ".svg"), "w") as fp:
            fp.write(output_svg)

        norm_name = replace_unicode(re.sub(r"[\s\(\),'-\.]", "", name))
        import_statements.append(
            'import UsState%sMap from "./assets/%s.svg";' % (norm_name, slug)
        )
        case_statements.append(
            """    case "%s":\n      return <UsState%sMap {...props} />;"""
            % (slug, norm_name)
        )

    script = STATE_SCRIPT % {
        "import_statements": "\n".join(import_statements),
        "case_statements": "\n".join(case_statements),
    }

    with open(os.path.join(outdir, "index.tsx"), "w") as fp:
        fp.write(script)


build_countries()
build_us_states()
