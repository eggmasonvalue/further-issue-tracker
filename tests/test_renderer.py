from pathlib import Path

from click.testing import CliRunner

from further_issue_tracker.cli import cli
from further_issue_tracker.renderer import discover_root_json_files, render_json_file


def test_render_json_file_creates_html(tmp_path: Path):
    source = Path("samples/pref_data.json")
    target = tmp_path / "pref_data.html"

    output = render_json_file(source, target)

    assert output == target
    html = target.read_text(encoding="utf-8")
    assert "<html lang=\"en\">" in html
    assert "pref_data.json" in html
    assert "Section" in html
    assert "APOLLO" in html


def test_discover_root_json_files_filters_data_artifacts(tmp_path: Path):
    (tmp_path / "pref_data.json").write_text("{}", encoding="utf-8")
    (tmp_path / "qip_data.json").write_text("{}", encoding="utf-8")
    (tmp_path / "notes.json").write_text("{}", encoding="utf-8")

    discovered = discover_root_json_files(tmp_path)

    assert discovered == [
        tmp_path / "pref_data.json",
        tmp_path / "qip_data.json",
    ]


def test_render_command_defaults_to_root_data_json_files(tmp_path: Path):
    runner = CliRunner()
    source = Path("samples/qip_data.json").read_text(encoding="utf-8")

    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        Path("qip_data.json").write_text(source, encoding="utf-8")
        result = runner.invoke(cli, ["render"], catch_exceptions=False)

        assert result.exit_code == 0
        rendered = Path("qip_data.html")
        assert rendered.exists()
        assert "E2E NETWORKS LIMITED" in rendered.read_text(encoding="utf-8")
