NAME = src/a_maze_ing.py
RUNNER = uv


install:
	@$(RUNNER) sync

run:
	@$(RUNNER) run $(NAME)

debug:
	@$(RUNNER) run python -m pdb $(NAME)

clean:
	@rm -rf src/*/__pycache__ .mypy_cache/ .venv/ uv.lock

lint:
	@flake8 src/
	@mypy src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@flake8 src/
	@mypy src/ --strict

.PHONY: install run debug clean lint lint-strict
