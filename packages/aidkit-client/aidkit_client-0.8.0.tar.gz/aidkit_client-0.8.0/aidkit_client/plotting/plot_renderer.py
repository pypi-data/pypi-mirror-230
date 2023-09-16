"""
Vega and Vega-Lite renderer specific to aidkit.

Generate a HTML container with custom styling to make the controls of
the plots nicer.
"""

import json
import uuid

from altair.vegalite.v4.display import VEGA_VERSION, VEGAEMBED_VERSION, VEGALITE_VERSION

# Additional styling for the plot controls
_AIDKIT_VIS_STYLE = r"""
    <style>
        div.aidkit-vis form.vega-bindings {
            display: block;
            width: 600px;
            padding-top: 5px;
        }

        div.aidkit-vis form.vega-bindings div.vega-bind {
            margin-bottom: 5px;
        }

        div.aidkit-vis form.vega-bindings span.vega-bind-name {
            text-align: right;
            width: 120px;
            display: inline-block;
            padding-right: 5px;
        }

        div.aidkit-vis form.vega-bindings input[type=range] {
            width: 150px;
            display: inline-block;
            margin-right: 5px;
        }

        div.aidkit-vis form.vega-bindings select {
            width: 334px;
            padding: 2px;
        }

        div.aidkit-vis form.vega-bindings span.vega-bind-radio {
            width: 250px;
        }

        div.aidkit-vis form.vega-bindings span.vega-bind-radio input{
            margin: 5px;
        }

        div.aidkit-vis form.vega-bindings span.vega-bind-radio label{
            margin-right: 10px;
        }

    </style>
"""


def _get_html(spec: dict, style: str, div_id: str) -> str:
    """
    Generate the HTML container that will contain the plot.

    :param spec: Dictionary containing the VEGA specification for the chart.
    :param style: HTML style element containing the CSS for the customized chart controls.
    :param div_id: Unique identifier for the div element in which the chart is rendered.

    :returns: String containing the HTML encoding of the chart.
    """
    return f"""
        {style}
        <body>

            <div id="vis-{div_id}" class="aidkit-vis"></div>

            <script type="text/javascript">
                var spec = {json.dumps(spec)};

                requirejs.config({{
                baseUrl: 'https://cdn.jsdelivr.net/npm/',
                paths: {{
                    "vega-embed":  "vega-embed@{VEGAEMBED_VERSION}?noext",
                    "vega-lib": "vega-lib@{VEGA_VERSION}?noext",
                    "vega-lite": "vega-lite@{VEGALITE_VERSION}?noext",
                    "vega": "vega@{VEGA_VERSION}?noext"
                    }}
                }});

                requirejs(["vega", "vega-embed"], function(vega, vegaEmbed) {{
                    vegaEmbed('#vis-{div_id}', spec).then(function(result) {{
                        }}).catch(console.error);
                    }});
            </script>
        </body>"""


def aidkit_altair_plot_renderer(spec: dict) -> dict:
    """
    Custom renderer for a Vega chart.

    :param spec: Dictionary containing the Vega specification of a chart.
    :return: Dictionary with representation of the given chart in plain text, HTML and Vega-Lite.
    """
    bundle = {}
    div_id = str(uuid.uuid4())
    bundle["text/html"] = _get_html(spec=spec, style=_AIDKIT_VIS_STYLE, div_id=div_id)
    bundle["text/plain"] = "<VegaLite 4 object - aidkit interractive chart>"
    return bundle
