from django.contrib import admin
from django.utils.html import format_html

from common.models import TimeStampedUUIDModel


class TimeStampedUUIDAdmin(admin.ModelAdmin):
    readonly_fields: tuple = ("created_at", "updated_at", "read_only_custom_id")
    list_display: tuple = ("id", "list_display_custom_id")
    list_per_page = 25

    def list_display_custom_id(self, obj: TimeStampedUUIDModel) -> str:
        return format_html(
            """
            <input type="text" value="{id}" id="id_{id}" hidden>
            <button type="button" onclick="copyUUID('id_{id}')"
            class="button copy-button" style="width: 24px;height:24px;">📋</button>
            <script>
                function copyUUID(elementId) {{
                    const input = document.getElementById(elementId);
                    const button = document.querySelector('.copy-button');
                    navigator.clipboard.writeText(input.value).then(function() {{
                        button.innerText = '✔';
                        setTimeout(() => {{
                            button.innerText = '📋';
                        }}, 1000);
                    }}).catch(function(err) {{
                        console.error('Failed to copy: ', err);
                    }});
                }}
            </script>
            """,
            id=obj.id,
        )

    list_display_custom_id.short_description = ""

    def read_only_custom_id(self, obj: TimeStampedUUIDModel) -> str:
        return format_html(
            """
            <input type="text" value="{id}" id="id_{id}" readonly style="width: 250px; border: none;">
            <button type="button" onclick="copyUUID('id_{id}')"
                    class="button copy-button" style="width: 24px;height:24px;">📋</button>
            <script>
                function copyUUID(elementId) {{
                    const input = document.getElementById(elementId);
                    const button = document.querySelector('.copy-button');
                    navigator.clipboard.writeText(input.value).then(function() {{
                        button.innerText = '✔';
                        setTimeout(() => {{
                            button.innerText = '📋';
                        }}, 1000);
                    }}).catch(function(err) {{
                        console.error('Failed to copy: ', err);
                    }});
                }}
            </script>
            """,
            id=obj.id,
        )

    read_only_custom_id.short_description = "UUID"
