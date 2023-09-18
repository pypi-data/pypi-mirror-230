import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    BlockElementHandler,
    InlineStyleElementHandler,
)


@hooks.register("register_rich_text_features", order=1)
def blockquote_editor_feature(features):
    """Register the `blockquote` feature.

    This uses the `blockquote` Draft.js block type, and is stored as HTML with
    a `<blockquote>` tag.
    """
    feature_name = "blockquote"
    type_ = "blockquote"
    tag = "blockquote"

    control = {
        "type": type_,
        "label": "❝",
        "description": "Quote",
        "element": "blockquote",
    }

    features.register_editor_plugin(
        "draftail",
        feature_name,
        draftail_features.BlockFeature(
            control,
        ),
    )

    features.register_converter_rule(
        "contentstate",
        feature_name,
        {
            "from_database_format": {
                tag: BlockElementHandler(
                    type_,
                ),
            },
            "to_database_format": {
                "block_map": {
                    type_: tag,
                },
            },
        },
    )
    features.default_features.append(feature_name)


@hooks.register("register_rich_text_features", order=1)
def inlinecode_editor_feature(features):
    feature_name = "Code Line"
    type_ = "CODE"
    tag = "code"

    control = {
        "type": type_,
        "label": ">_",
        "description": "Code Line",
    }

    features.register_editor_plugin(
        "draftail",
        feature_name,
        draftail_features.InlineStyleFeature(
            control,
        ),
    )

    db_conversion = {
        "from_database_format": {
            tag: InlineStyleElementHandler(
                type_,
            ),
        },
        "to_database_format": {
            "style_map": {
                type_: tag,
            },
        },
    }

    features.register_converter_rule("contentstate", feature_name, db_conversion)
    features.default_features.append(feature_name)


@hooks.register("insert_editor_css", order=1)
def fix_fieldset():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static("wagtail_sb_blocks/css/fieldset_fix.css"),
    )
