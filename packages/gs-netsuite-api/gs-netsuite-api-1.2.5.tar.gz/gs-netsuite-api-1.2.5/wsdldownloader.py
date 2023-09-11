#! /usr/bin/env python
from __future__ import annotations, print_function

import dataclasses
import os
import shutil
import urllib.parse as urlparse
import urllib.request as urlrequest
from functools import cached_property
from pathlib import Path
from typing import Optional
from xml.dom import minidom

import src.gs_netsuite_api.ns_utils as ns_utils

INDENT_LEVEL = 2


@dataclasses.dataclass
class ArgsDT:
    wsdl_url: str = ""
    output_dir: str = ""


def xml_to_pretty_string(xml):
    text = xml.toprettyxml(indent=" " * INDENT_LEVEL)
    not_empty_lines = [line for line in (text.splitlines()) if (line and not line.isspace())]
    return "\n".join(not_empty_lines)


@dataclasses.dataclass
class XsdDocument:
    uri: str
    output: Path
    parent: Optional[XsdDocument] = None

    @cached_property
    def wsdl_doc(self) -> minidom.Document:
        return self.read_xml_from_url()

    def read_xml_from_url(self) -> minidom.Document:
        print("Reading", urlparse.urlunparse(self.remote_url))
        text = urlrequest.urlopen(urlparse.urlunparse(self.remote_url)).read()
        return minidom.parseString(text)

    @cached_property
    def remote_url(self) -> urlparse.ParseResult:
        xsd_url_parsed = urlparse.urlparse(self.uri)
        if not xsd_url_parsed.scheme or not xsd_url_parsed.netloc:
            # It'a a relative path to wsdl_info.wsdl_url
            path_wsdl, filename = os.path.split(self.parent.remote_url.path)
            return urlparse.ParseResult(
                scheme=self.parent.remote_url.scheme,
                netloc=self.parent.remote_url.netloc,
                params=xsd_url_parsed.params,
                query=xsd_url_parsed.query,
                fragment=xsd_url_parsed.fragment,
                path=os.path.join(path_wsdl, self.uri),
            )
        return urlparse.urlparse(self.uri)

    def download(self):
        dir, filename = self.download_path()
        print("mkdir  ", dir)
        os.makedirs(dir, exist_ok=True)
        content = xml_to_pretty_string(self.read_xml_from_url())
        final_path = os.path.join(dir, filename)
        print("Writing", final_path)
        with open(final_path, "w") as f:
            f.write(content)

    def exists(self):
        return os.path.exists(os.path.join(*self.download_path()))

    def download_path(self) -> (str, str):
        wsdl_path, filename = os.path.split(urlparse.urlparse(self.uri).path)
        dir_dest = self.output.resolve()
        wsdl_path = wsdl_path.removeprefix(os.sep)
        wsdl_path = dir_dest.joinpath(wsdl_path)
        wsdl_path = wsdl_path.resolve()
        return wsdl_path, filename

    def create_child(self, uri: str) -> XsdDocument:
        return XsdDocument(uri=uri, parent=self, output=self.download_path()[0])


def download_xsd_imports(rootDoc: XsdDocument, xml_schema_mapping="xsd:"):
    xsd_import_elems = rootDoc.wsdl_doc.getElementsByTagName(xml_schema_mapping + "import")
    for elem in xsd_import_elems:
        schema_location = elem.attributes.get("schemaLocation")
        doc = rootDoc.create_child(uri=schema_location.value)
        if doc.exists():
            continue
        doc.download()
        download_xsd_imports(doc, xml_schema_mapping="")
        download_xsd_imports(doc, xml_schema_mapping="xsd:")


def main():
    ns = ns_utils.NetSuiteCredential.from_env_file("./auth_netsuite.env").get_netSuite()
    output_dir = Path("output").resolve()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    rootDoc = XsdDocument(uri=ns.soap_api.wsdl_url, output=output_dir, parent=None)
    rootDoc.download()
    download_xsd_imports(rootDoc)
    download_xsd_imports(rootDoc, xml_schema_mapping="xsd:")


if __name__ == "__main__":
    main()
