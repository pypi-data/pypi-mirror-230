#!/bin/env python
################################################################
import streamlit as st
import yaml

from solidipes.metadata import lang
from solidipes.metadata import licences_data_or_software as licenses
from solidipes.utils import get_study_metadata, set_study_metadata

from .custom_widgets import EditProgBox, EditTextBox
from .git_infos import GitInfos

################################################################


class ZenodoInfos(GitInfos):
    def __init__(self, layout):
        super().__init__()
        self.layout = layout
        self.layout = layout.container()
        # self.global_message = global_message
        self.zenodo_metadata = get_study_metadata()

    def saveZenodoEntry(self, key, value):
        self.zenodo_metadata[key] = value
        set_study_metadata(self.zenodo_metadata)

    def save_description(self, value):
        self.zenodo_metadata["description"] = value
        set_study_metadata(self.zenodo_metadata)

    def show_upload_type(self):
        options = [
            "publication",
            "poster",
            "presentation",
            "dataset",
            "image",
            "video",
            "software",
            "lesson",
            "physicalobject",
            "other",
        ]
        value = self.zenodo_metadata["upload_type"]
        selected = st.selectbox("Upload type", options=options, index=options.index(value))
        if selected != value:
            self.saveZenodoEntry("upload_type", selected)

    def show_license(self):
        options = [_l[0] for _l in licenses]
        fmt_map = dict(licenses)

        value = self.zenodo_metadata["license"]
        selected = st.selectbox(
            "License", options=options, index=options.index(value), format_func=lambda x: fmt_map[x] + f" ({x})"
        )
        if selected != value:
            self.saveZenodoEntry("license", selected)

    def show_language(self):
        options = [_l[0] for _l in lang]
        fmt_map = dict(lang)

        value = self.zenodo_metadata["language"]
        selected = st.selectbox(
            "Language", options=options, index=options.index(value), format_func=lambda x: fmt_map[x]
        )
        if selected != value:
            self.saveZenodoEntry("language", selected)

    def show_keywords(self):
        k_text = ", ".join(self.zenodo_metadata["keywords"])
        EditTextBox(
            k_text,
            caption="Keywords",
            fmt="<b>Keywords:</b> " + k_text,
            key="keywords",
            on_apply=lambda x: self.saveZenodoEntry("keywords", [e.strip() for e in x.split(",")]),
        )

    def format_authors(self, authors):
        orcid_img = '<img height="15" src="https://zenodo.org/static/img/orcid.png">'
        authors = []
        affiliations = []
        for auth in self.zenodo_metadata["creators"]:
            if "affiliation" in auth:
                aff = auth["affiliation"].split(",")
                for e in aff:
                    if e.strip() not in affiliations:
                        affiliations.append(e.strip())

        for auth in self.zenodo_metadata["creators"]:
            text = ""
            if "orcid" in auth:
                text += f'<a href="https://orcid.org/{auth["orcid"]}">{orcid_img}</a> '
            if "name" in auth:
                text += f'**{auth["name"]}**'
            if "affiliation" in auth:
                text += "$^{"
                aff = auth["affiliation"].split(",")
                aff = [affiliations.index(e.strip()) + 1 for e in aff]
                aff = [str(e) for e in aff]
                text += f'{",".join(aff)}'
                text += "}$"

            authors.append(text)
        formatted = "**<center> " + ", ".join(authors) + " </center>**\n"
        for idx, aff in enumerate(affiliations):
            formatted += f"<center><sup>{idx+1}</sup> <i>{aff}</i></center>\n"
        return formatted

    def show_creators(self):
        yaml_authors = yaml.safe_dump(self.zenodo_metadata["creators"])

        def save_creators(x):
            try:
                _yaml = yaml.safe_load(x)
                for e in _yaml:
                    if "name" not in e:
                        raise RuntimeError("An author needs mandatorily a name")
                self.saveZenodoEntry("creators", _yaml)
            except yaml.parser.ParserError:
                raise RuntimeError("Invalid yaml file: did you check the indentation ?")

        EditTextBox(yaml_authors, caption="Authors", fmt=self.format_authors, key="creators", on_apply=save_creators)

    def show_doi(self):
        value = ""
        if "doi" in self.zenodo_metadata:
            value = self.zenodo_metadata["doi"]

        content = st.text_input("DOI", value=value, placeholder="put a reserved doi if you have one")
        if content != "":
            self.saveZenodoEntry("doi", content)

    def show_relations(self, rels, block, update_rel):
        block_container = block.container()
        type_options = [
            "publication-annotationcollection",
            "publication-book",
            "publication-section",
            "publication-conferencepaper",
            "publication-datamanagementplan",
            "publication-article",
            "publication-patent",
            "publication-preprint",
            "publication-deliverable",
            "publication-milestone",
            "publication-proposal",
            "publication-report",
            "publication-softwaredocumentation",
            "publication-taxonomictreatment",
            "publication-technicalnote",
            "publication-thesis",
            "publication-workingpaper",
            "publication-other",
            "software",
        ]
        rel_options = [
            "isCitedBy",
            "cites",
            "isSupplementTo",
            "isSupplementedBy",
            "isContinuedBy",
            "continues",
            "isDescribedBy",
            "describes",
            "hasMetadata",
            "isMetadataFor",
            "isNewVersionOf",
            "isPreviousVersionOf",
            "isPartOf",
            "hasPart",
            "isReferencedBy",
            "references",
            "isDocumentedBy",
            "documents",
            "isCompiledBy",
            "compiles",
            "isVariantFormOf",
            "isOriginalFormof",
            "isIdenticalTo",
            "isAlternateIdentifier",
            "isReviewedBy",
            "reviews",
            "isDerivedFrom",
            "isSourceOf",
            "requires",
            "isRequiredBy",
            "isObsoletedBy",
            "obsolete",
        ]

        for i, r in enumerate(rels):
            _left, _type, _id = block_container.columns(3)
            but, _rel = _left.columns(2)
            but.button("➖", on_click=lambda: update_rel(i, delete=True), key=f'del_but_{i}_{r["identifier"]}')
            _t = _type.selectbox(
                "Type",
                options=type_options,
                index=type_options.index(r["resource_type"]),
                label_visibility="collapsed",
                key=f'type_{i}_{r["identifier"]}',
            )
            _i = _id.text_input(
                "id/url", value=r["identifier"], label_visibility="collapsed", key=f'id_{i}_{r["identifier"]}'
            )
            _r = _rel.selectbox(
                "Relation",
                options=rel_options,
                index=rel_options.index(r["relation"]),
                label_visibility="collapsed",
                key=f'rel_{i}_{r["identifier"]}',
            )
            update_rel(i, update=(_r, _t, _i))

    def show_related_identifiers(self):
        rels = []
        if "related_identifiers" in self.zenodo_metadata:
            rels = self.zenodo_metadata["related_identifiers"]

        block = st.empty()
        if "redraw" not in st.session_state:
            st.session_state["redraw"] = False

        def update(i, delete=False, update=None):
            if delete:
                del rels[i]
            if update is not None:
                _r, _t, _i = update
                rels[i] = {"identifier": _i, "relation": _r, "resource_type": _t}

            self.saveZenodoEntry("related_identifiers", rels)
            st.session_state["redraw"] = True

        if st.session_state["redraw"] is True:
            block.empty()
            st.session_state["redraw"] = False

        if st.button("➕ New relation"):
            rels.append({"identifier": "", "relation": "isCitedBy", "resource_type": "publication-article"})
            self.saveZenodoEntry("related_identifiers", rels)
            st.session_state["redraw"] = True
            block.empty()

        self.show_relations(rels, block, update)

    def textbox(self, key, **kwargs):
        EditTextBox(self.zenodo_metadata[key], caption=key.capitalize(), key=key, **kwargs)

    def description_box(self, **kwargs):
        desc = self.zenodo_metadata["description"]
        with st.expander("**Description (README.md is a generated file: do not edit manually)**", expanded=True):
            if self.git_origin:
                url = self.git_origin + "/-/edit/master/DESCRIPTION.md"
                st.markdown(f"[Edit on Gitlab]({url})", unsafe_allow_html=True)
            EditProgBox(desc, language="markdown", key="description", on_apply=self.save_description, **kwargs)

    def show(self):
        with self.layout:
            self._show()

    def _show(self):
        self.textbox("title", fmt="## <center> {0} </center>", on_apply=lambda x: self.saveZenodoEntry("title", x))

        self.show_creators()
        self.show_keywords()
        with st.expander("**General Metadata**", expanded=False):
            self.show_upload_type()
            self.show_license()
            self.show_language()
            self.show_doi()
        with st.expander("**Additional Relations**", expanded=False):
            self.show_related_identifiers()
        self.description_box()
        self.raw_editor()

    def raw_editor(self):
        with self.layout.expander("**Additional Raw Metadata** (Zenodo YAML format)", expanded=False):
            st.markdown("You can edit the metadata below")
            st.markdown(
                "*Description of the Zenodo metadata can be found"
                " [here](https://github.com/zenodo/developers.zenodo.org"
                "/blob/master/source/includes/resources/deposit/"
                "_representation.md#deposit-metadata)*"
            )
            st.markdown("---")

            zenodo_metadata = get_study_metadata()
            metadata = zenodo_metadata.copy()

            for k in [
                "title",
                "creators",
                "keywords",
                "language",
                "upload_type",
                "license",
                "description",
                "related_identifiers",
            ]:
                if k in metadata:
                    del metadata[k]
            if metadata:
                zenodo_content = yaml.safe_dump(metadata)
            else:
                zenodo_content = ""

            def save(x):
                metadata = yaml.safe_load(x)
                zenodo_metadata.update(metadata)
                set_study_metadata(zenodo_metadata)

            EditProgBox(
                zenodo_content, language="yaml", disable_view=True, on_apply=lambda x: save(x), key="zenodo_raw"
            )


################################################################


class WebProgressBar:
    def __init__(self, layout, filename, size):
        self.layout = layout
        self.bar = self.layout.progress(0, text="Upload Archive to **Zenodo**")
        self.filename = filename
        self.size = size
        self.uploaded = 0

    def close(self):
        self.layout.empty()

    def update(self, x):
        self.uploaded += x
        percent_complete = self.uploaded * 100 // self.size
        self.bar.progress(
            percent_complete,
            text=f"Upload Archive to **Zenodo {percent_complete}%**",
        )


################################################################


class ZenodoPublish:
    def __init__(self, layout, global_message, progress_layout):
        self.layout = layout
        self.layout = layout.container()
        self.global_message = global_message
        self.progress_layout = progress_layout

    def show(self):
        self.layout.markdown("")
        with self.layout.expander("Publish in Zenodo", expanded=True):
            token = st.text_input("Zenodo token", type="password")
            dry_run = st.checkbox("sandbox", value=True)
            new_deposition = st.checkbox("Don't use existing deposition", value=False)
            zenodo_metadata = get_study_metadata()
            existing_identifier = False
            if "doi" in zenodo_metadata and not new_deposition:
                existing_identifier = zenodo_metadata["doi"]

            col1, col2 = st.columns(2)
            title = "Submit as draft to Zenodo sandbox"
            if not dry_run:
                title = "Submit as draft to Zenodo"
                col2.markdown(
                    "**Not using sandbox will submit to the main "
                    "Zenodo website. Please push content with caution "
                    "as it may result in a permanent entry**"
                )

            def submit():
                st.session_state.zenodo_publish = []
                try:
                    self.zenodo_upload(token, existing_identifier, sandbox=dry_run, new_deposition=new_deposition)
                except Exception as e:
                    self.global_message.error("upload error" + str(e))

            col1.button(title, type="primary", on_click=submit)

            if "zenodo_publish" in st.session_state and st.session_state.zenodo_publish:
                print(st.session_state.zenodo_publish)
                st.code("\n".join(st.session_state.zenodo_publish).replace("[94m", "").replace("[0m", ""))

    def _print(self, val):
        st.session_state.zenodo_publish.append(val)

    def zenodo_upload(self, access_token, existing_identifier, sandbox=True, new_deposition=False):
        import argparse

        import solidipes.scripts.upload as upload

        args = argparse.Namespace()
        args.access_token = access_token
        args.sandbox = sandbox
        args.directory = None
        args._print = self._print
        args.new_deposition = new_deposition
        args.existing_identifier = existing_identifier
        upload._main(args, progressbar=lambda filename, size: WebProgressBar(self.progress_layout, filename, size))
