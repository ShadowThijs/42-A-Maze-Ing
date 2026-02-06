NAME = src/a_maze_ing.py
RUNNER = uv


install:
	@$(RUNNER) sync

run:
	@$(RUNNER) run $(NAME)

debug:
	@$(RUNNER) run python -m pdb $(NAME)

clean:

lint:
	@flake8 src/
	@mypy src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@flake8 src/
	@mypy src/ --strict

