from common.models import TimeStampedUUIDModel


def test_id_default_generates_uuid7() -> None:
    default = TimeStampedUUIDModel._meta.get_field("id").default

    assert default().version == 7
