NAME = src/a_maze_ing.py
CONFIG = config.txt
RUNNER = uv


install:
	@$(RUNNER) sync
	@make -C mlx_CLXV/
	@$(RUNNER) pip install mlx_CLXV/mlx-2.2-py3-none-any.whl


run:
	@$(RUNNER) run $(NAME) $(CONFIG)

debug:
	@$(RUNNER) run python -m pdb $(NAME) $(CONFIG)

clean:
	@rm -rf src/*/__pycache__ .mypy_cache/ .venv/ uv.lock mazegen_pkg/dist mazegen_pkg/*.egg-info

lint:
	@flake8 src/
	@mypy src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@flake8 src/
	@mypy src/ --strict

build-pkg:
	@cd mazegen_pkg && $(RUNNER) build
	@cp mazegen_pkg/dist/mazegen-*.whl .

.PHONY: install run debug clean lint lint-strict build-pkg
