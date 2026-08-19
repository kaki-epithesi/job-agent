from pathlib import Path

from job_agent.config.resume import load_resume


def test_load_resume_from_file(tmp_path: Path):
    path = tmp_path / "resume.yaml"
    path.write_text(
        "skills:\n  - python\n  - docker\nroles:\n  - backend engineer\n",
        encoding="utf-8",
    )

    resume = load_resume(path)

    assert resume.skills == ["python", "docker"]
    assert resume.roles == ["backend engineer"]
    assert resume.keywords == []
    assert resume.locations == []


def test_load_resume_default():
    resume = load_resume()
    assert isinstance(resume.skills, list)
    assert len(resume.skills) > 0


def test_load_resume_target_roles(tmp_path: Path):
    path = tmp_path / "resume.yaml"
    path.write_text(
        "target_roles:\n  - engineer\n  - developer\n",
        encoding="utf-8",
    )

    resume = load_resume(path)

    assert resume.target_roles == ["engineer", "developer"]
