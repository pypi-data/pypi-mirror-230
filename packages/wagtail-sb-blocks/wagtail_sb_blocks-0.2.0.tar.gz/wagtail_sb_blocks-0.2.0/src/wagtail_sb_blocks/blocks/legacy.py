from django.conf import settings
from django.db.models import TextChoices
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    ListBlock,
    PageChooserBlock,
    RawHTMLBlock,
    RichTextBlock,
    StreamBlock as LegacyStreamBlock,
    TextBlock,
    URLBlock,
)
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images import get_image_model
from wagtail.images.blocks import ImageChooserBlock
from wagtail_sb_imageserializer.api.fields import ImageSerializerField
from wagtail_sb_structblock.blocks import StructBlock

__all__ = [
    "H1",
    "H2",
    "H3",
    "H4",
    "H5",
    "H6",
    "Paragraph",
    "Figure",
    "OrderedList",
    "UnorderedList",
    "Button",
    "HTMLBlock",
]


RICH_TEXT_FIELD_FREATURES = [
    "bold",
    "italic",
    "code",
    "link",
    "document-link",
]


class EmbedRatio(TextChoices):
    RATIO_16_9 = "ratio-16-9", "16:9"
    RATIO_4_3 = "ratio-4-3", "4:3"

    __empty__ = _("Without ratio")


class ButtonSize(TextChoices):
    SMALL = "small", _("Small")
    LARGE = "large", _("Large")

    __empty__ = _("Normal")


class StreamBlock(LegacyStreamBlock):
    """Override Wagtail's `StreamBlock`.

    Replacement for the Wagtail 'StreamBlock' which prevents the appearance
    of the annoying 'div' class 'block-<block-type>' around 'StreamBlock'
    children contents
    """

    def render_basic(self, value, context=None):
        return format_html_join(
            "\n",
            "{0}",
            [(child.render(context=context), child.block_type) for child in value],
        )


class H1(CharBlock):
    """Block for H1 titles."""

    class Meta:
        label = "H1"
        icon = "title"


class H2(CharBlock):
    """Block for H2 titles."""

    class Meta:
        label = "H2"
        icon = "title"


class H3(CharBlock):
    """Block for H3 titles."""

    class Meta:
        label = "H3"
        icon = "title"


class H4(CharBlock):
    """Block for H4 titles."""

    class Meta:
        label = "H4"
        icon = "title"


class H5(CharBlock):
    """Block for H5 titles."""

    class Meta:
        label = "H5"
        icon = "title"


class H6(CharBlock):
    """Block for H6 titles."""

    class Meta:
        label = "H6"
        icon = "title"


class Paragraph(RichTextBlock):
    """Block for paragraphs."""

    def __init__(self, **kwargs):
        kwargs["features"] = RICH_TEXT_FIELD_FREATURES

        super().__init__(**kwargs)

    class Meta:
        label = _("parragrah")
        icon = "form"


class Figure(StructBlock):
    """Block for figures.

    With it's respective caption. On render this genrates a
    <figure> element, if no caption is provided only and <img> is generated.
    """

    images = ListBlock(
        ImageChooserBlock(
            labe=_("Images"),
        ),
    )

    caption = Paragraph(
        label=_("Legend"),
        required=False,
    )

    class Meta:
        label = _("Figure")
        icon = "image"

    def get_api_representation(self, value, context=None):
        api_representation = super().get_api_representation(value, context)
        if api_representation is None:
            api_representation = {}

        # api_module = importlib.import_module("api.v1.views.wagtail.images")

        # view = api_module.ImagesAPIViewSet
        model = get_image_model()
        # router = context["router"]
        # serializer_images = ImageSerializerField(
        #     renditions={
        #         "list": "fill-300x300",
        #         "card": "fill-200x200",
        #     }
        # )
        serializer_images = ImageSerializerField(
            renditions=settings.RENDITIONS["wagtail_sb_block.blocks.Figure.images"]
        )
        queryset = model.objects.filter(id__in=api_representation["images"])

        # serializer_class = view._get_serializer_class(
        #     router, model, [("*", False, None)]
        # )
        # serializer = serializer_class( queryset, context=context, many=True)

        api_representation["images"] = [
            serializer_images.to_representation(image) for image in queryset
        ]

        return api_representation


class Quote(StructBlock):
    """Block for quote.

    With it's respective caption. On render this genrates a
    <figure> element, if no caption is provided only and <img> is generated.
    """

    text = Paragraph(
        label=_("Quote"),
    )
    author = CharBlock(
        label=_("Author"),
        required=False,
    )

    class Meta:
        label = _("Quote")
        icon = "openquote"


class OrderedList(ListBlock):
    class Meta:
        label = _("Ordered list")
        icon = "list-ol"


class UnorderedList(ListBlock):
    class Meta:
        label = _("Unordered list")
        icon = "list-ul"


class Button(StructBlock):
    text = CharBlock(
        label=_("Text"),
    )
    link = URLBlock(
        label=_("External link"),
        required=False,
    )
    page = PageChooserBlock(
        label=_("Link to page"),
        required=False,
    )
    document = DocumentChooserBlock(
        label=_("Link to document"),
        required=False,
    )
    size = ChoiceBlock(
        label=_("Size"),
        required=False,
        choices=ButtonSize.choices,
        default=None,
    )

    custom_id = CharBlock(
        required=False,
        max_length=255,
        label=_("Custom ID"),
    )
    tracking_event_category = CharBlock(
        required=False,
        max_length=255,
        label=_("Tracking Event Category"),
    )
    tracking_event_label = CharBlock(
        required=False,
        max_length=255,
        label=_("Tracking Event Label"),
    )

    class Meta:
        label = _("Button")
        icon = "placeholder"
        settings_fields = [
            "size",
            "custom_id",
            "tracking_event_category",
            "tracking_event_label",
        ]

    def get_api_representation(self, value, context=None):
        api_representation = super().get_api_representation(value, context)
        page = value.get("page", None)

        if page is not None:
            page = page.specific
            page_type = f"{page._meta.app_label}.{type(page).__name__}"

            api_representation["page"] = {
                "id": page.id,
                "meta": {
                    "slug": page.slug,
                    "type": page_type,
                },
                "title": page.title,
            }

        document = value.get("document", None)
        if document is not None:
            document_type = f"{document._meta.app_label}.{type(document).__name__}"
            api_representation["document"] = {
                "id": document.id,
                "meta": {
                    "type": document_type,
                    "download_url": document.file.url,
                },
                "title": document.title,
            }

        return api_representation


class Code(StructBlock):
    # help_text with mark_safe are intended to display some html tags with
    # predefined content by the team
    language = CharBlock(
        label=_("Language"),
        required=True,
        help_text=mark_safe(  # nosec
            _(
                "Consulta lista de lenguajes soportados "
                "<a href='https://prismjs.com/#supported-languages'target='_blank'>"
                "Prism.js</a>"
            )
        ),
    )
    code = TextBlock(
        label=_("Code"),
        required=True,
        classname="monotype",
    )

    caption = Paragraph(
        label=_("Legend"),
        required=False,
    )

    class Meta:
        label = _("Code")
        icon = "code"


class Equation(TextBlock):
    class Meta:
        label = _("Equation")
        icon = "superscript"
        classname = "monotype"


class Embed(StructBlock):
    embed_object = EmbedBlock(
        label=_("URL"),
        required=False,
        help_text=_("Url's to embed content from other sites compatible with oembed."),
        classname="embed-inner-wrapper",
    )

    embed_raw = RawHTMLBlock(
        label=_("HTML"),
        required=False,
        help_text=_("Insert snippet to embed content from other sites."),
    )

    caption = Paragraph(
        label=_("Legend"),
        required=False,
    )

    embed_ratio = ChoiceBlock(
        label=_("Aspect ratio"),
        required=False,
        choices=EmbedRatio.choices,
        default=None,
    )

    class Meta:
        label = _("Embed")
        icon = "media"

    def get_api_representation(self, value, context=None):
        api_representation = super().get_api_representation(value, context)

        embed_object = value.get("embed_object", None)
        if embed_object is not None:
            api_representation["embed_object"] = {
                "html": embed_object.html,
                "url": embed_object.url,
            }

        return api_representation


class HTMLBlock(RawHTMLBlock):
    class Meta:
        label = _("HTML")
        icon = "code"
