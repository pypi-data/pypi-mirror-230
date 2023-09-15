# These functions should be reworked in the future to use the companies service

import asyncio
from bson.objectid import ObjectId
from delphai_ml_utils.db import db, db_sync

tech_major_layers = {
    "display": "5fad13fec883a62ab3de75f3",
    "calculated": "5fad13ffc883a62ab3de75f4",
    "added": "5fad13ffc883a62ab3de75f5",
    "removed": "5fad13ffc883a62ab3de75f6",
}
tech_minor_layers = {
    "display": "5fad13ffc883a62ab3de75f7",
    "calculated": "5fad13ffc883a62ab3de75f8",
    "added": "5fad13ffc883a62ab3de75f9",
    "removed": "5fad13ffc883a62ab3de75fa",
}
industry_layers = {
    "display": "5eeb429e0faf396f69e26056",
    "calculated": "5fad13fec883a62ab3de75f0",
    "added": "5fad13fec883a62ab3de75f1",
    "removed": "5fad13fec883a62ab3de75f2",
}
industry_search_layers = {
    "display": "62442ea35e4d371fa97de7ef",
    "calculated": "62442ea35e4d371fa97de7f2",
    "added": "62442ea35e4d371fa97de7f0",
    "removed": "62442ea35e4d371fa97de7f1",
}
layers_mapping = {
    "tech_major": tech_major_layers,
    "tech_minor": tech_minor_layers,
    "industry": industry_layers,
    "industry_search": industry_search_layers,
}


async def get_type_labels(label_type, layer):
    to_return = {}
    async for el in db.labels.find(
        {"layer_id": ObjectId(layers_mapping[label_type][layer])}
    ):
        to_return[el["_id"]] = el["name"]
    return to_return


async def get_company_labels(company_id, labels):
    to_return = []
    async for el in db.companies_labels.find(
        {"company_id": company_id, "label_id": {"$in": list(labels.keys())}},
        sort=[["score", -1], ["rank", -1]],
    ):
        to_return.append(labels[el["label_id"]])
    return to_return


async def get_all_company_labels(comp_id, all_labels):
    company_id = ObjectId(comp_id)
    labels_dict = {"_id": comp_id}
    tasks = []
    for labels in all_labels:
        tasks.append(get_company_labels(company_id, labels))
    awaited = await asyncio.gather(*tasks)
    for layer, response in zip(
        ["industry", "industry_search", "tech_major", "tech_minor"], awaited
    ):
        labels_dict[layer] = response
    return labels_dict


async def get_labels_for_companies(comp_ids, namespace_layer):
    tasks = [
        get_type_labels(label_type, namespace_layer)
        for label_type in ["industry", "industry_search", "tech_major", "tech_minor"]
    ]
    awaited = await asyncio.gather(*tasks)
    industry_labels = awaited[0]
    industry_search_labels = awaited[1]
    tech_major_labels = awaited[2]
    tech_minor_labels = awaited[3]
    all_labels = [
        industry_labels,
        industry_search_labels,
        tech_major_labels,
        tech_minor_labels,
    ]

    tasks = [get_all_company_labels(comp_id, all_labels) for comp_id in comp_ids]
    awaited = await asyncio.gather(*tasks)
    to_return = sorted(awaited, key=lambda x: x["_id"])

    return to_return


def get_labels_for_company(comp_id, namespace_layer):
    company_id = ObjectId(comp_id)
    industry_labels = {
        el["_id"]: el["name"]
        for el in db_sync.labels.find(
            {"layer_id": ObjectId(layers_mapping["industry"][namespace_layer])}
        )
    }
    tech_major_labels = {
        el["_id"]: el["name"]
        for el in db_sync.labels.find(
            {"layer_id": ObjectId(layers_mapping["tech_major"][namespace_layer])}
        )
    }
    tech_minor_labels = {
        el["_id"]: el["name"]
        for el in db_sync.labels.find(
            {"layer_id": ObjectId(layers_mapping["tech_minor"][namespace_layer])}
        )
    }
    industry_search_labels = {
        el["_id"]: el["name"]
        for el in db_sync.labels.find(
            {"layer_id": ObjectId(layers_mapping["industry_search"][namespace_layer])}
        )
    }

    labels_dict = {}
    for layer, labels in (
        ("industry", industry_labels),
        ("tech_major", tech_major_labels),
        ("tech_minor", tech_minor_labels),
        ("industry_search", industry_search_labels),
    ):
        labels_dict[layer] = [
            labels[el["label_id"]]
            for el in db_sync.companies_labels.find(
                {"company_id": company_id, "label_id": {"$in": list(labels.keys())}},
                sort=[["score", -1], ["rank", -1]],
            )
        ]
    return labels_dict


def get_labels_with_ids(label_type, namespace_layer="display"):
    layer_id = ObjectId(layers_mapping[label_type][namespace_layer])
    return {
        el["name"]: str(el["_id"]) for el in db_sync.labels.find({"layer_id": layer_id})
    }
