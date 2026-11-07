"""HTTP callback checks only; no browser, transport or instrument access."""


def post_callback(app, key, values, changed):
    callback = app.callback_map[key]
    outputs = [
        {"id": output.component_id, "property": output.component_property}
        for output in callback["output"]
    ]
    response = app.server.test_client().post(
        "/_dash-update-component",
        json={
            "output": key,
            "outputs": outputs,
            "changedPropIds": [changed],
            "inputs": [dict(item, value=values.get(item["id"])) for item in callback["inputs"]],
            "state": [dict(item, value=values.get(item["id"])) for item in callback["state"]],
        },
    )
    assert response.status_code == 200
    return response.get_json()["response"]
