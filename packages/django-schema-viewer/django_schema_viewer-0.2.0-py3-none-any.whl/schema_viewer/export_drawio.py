from io import BytesIO
from typing import Any
import xml.etree.ElementTree as ET


def make_edge(source: str, target: str):
    mx_cell = ET.Element('mxCell', attrib={
        'id': f'{source}-{target}',
        'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=ERoneToMany;endFill=0;curved=1;',
        'edge': '1',
        'parent': '1',
        'source': f'{source}',
        'target': f'{target}',
    })
    ET.SubElement(mx_cell, 'mxGeometry', attrib={'relative': '1', 'as': 'geometry'})
    return mx_cell


def make_table(table: dict[str, Any]):
    tfield = lambda field: f'<tr><td>{field["name"]}</td><td>{field["type"]}</td></tr>'
    html_tr: list[str] = list(map(tfield, table['schema']['fields']))
    html_header = f'<div align="center" style="box-sizing:border-box;width:100%;background:#e4e4e4;padding:2px;">{table["name"]}</div>'
    html_table = f'<table style="width:100%;font-size:1em" cellpadding="2" cellspacing="0">{"".join(html_tr)}</table>'
    mx_cell = ET.Element('mxCell', attrib={
        'id': table['name'],
        'value': f'{html_header}{html_table}',
        'style': "verticalAlign=top;align=left;overflow=fill;html=1;whiteSpace=wrap;strokeColor=none;shadow=1;",
        'vertex': "1",
        'parent': "1",
    })
    ET.SubElement(mx_cell, 'mxGeometry',
                  # attrib={'x': '330', 'y': '210', 'width': '180', 'height': '80', 'as': 'geometry'})
                  attrib={'width': '180', 'height': '80', 'as': 'geometry'})
    return mx_cell


def export(json_table_schema: dict[str, Any]) -> str:
    mxfile = ET.Element('mxfile', attrib=dict(
        host="app.diagrams.net",
        modified="2023-09-12T11:08:59.667Z",
        agent="Super agent",
        etag="doc1",
        version="21.7.2",
        type="device",
    ))
    root = ET.SubElement(
        ET.SubElement(
            ET.SubElement(
                mxfile,
                'diagram',
                attrib=dict(
                    name="page1",
                    id="diagram1",
                ),
            ),
            'mxGraphModel',
            attrib=dict(
                dx="1420",
                dy="752",
                grid="1",
                gridSize="10",
                guides="1",
                tooltips="1",
                connect="1",
                arrows="1",
                fold="1",
                page="1",
                pageScale="1",
                pageWidth="2000",
                pageHeight="1000",
                math="0",
                shadow="0",
            )
        ),
        'root'
    )
    ET.SubElement(root, 'mxCell', attrib=dict(id='0'))
    ET.SubElement(root, 'mxCell', attrib=dict(id='1', parent='0'))

    for table in json_table_schema['resources']:
        for field in table['schema']['foreignKeys']:
            root.append(make_edge(field['reference']['resource'], table['name']))
        root.append(make_table(table))

    tree = ET.ElementTree(mxfile)
    with BytesIO() as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)
        return f.getvalue().decode('utf-8')

