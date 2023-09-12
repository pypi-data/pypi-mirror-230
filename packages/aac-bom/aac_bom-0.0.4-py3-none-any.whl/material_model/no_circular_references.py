"""AaC validator implementation module for specification req reference ids."""
import logging

from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


CIRCULAR_REF_VALIDATOR_NAME = "No circular material references"

site_tree = {}
assembly_tree = {}


def validate_no_circluar_material_refs(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validates that the referenced requirement id exists within the context.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.
        *validation_args: The names of the required fields.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    _get_site_tree(language_context)
    _get_assembly_tree(language_context)

    # check sites for cycles
    site_roots = language_context.get_definitions_by_root_key("site")
    for root in site_roots:
        dupe = _look_for_dupes(root.name, [], site_tree)
        if dupe:
            lexeme = root.get_lexeme_with_value(dupe)
            message = f"Circular site reference detected for {dupe} in {lexeme.source} on line {lexeme.location.line + 1}"

            findings.add_error_finding(definition_under_test, message, CIRCULAR_REF_VALIDATOR_NAME, lexeme)
            logging.debug(message)

    # check assemblies for cycles
    assembly_roots = language_context.get_definitions_by_root_key("assembly")
    for root in assembly_roots:

        dupe = _look_for_dupes(root.name, [], assembly_tree)
        if dupe:
            lexeme = root.get_lexeme_with_value(dupe)
            message = f"Circular assembly reference detected for {dupe} in {lexeme.source} on line {lexeme.location.line + 1}"

            findings.add_error_finding(definition_under_test, message, CIRCULAR_REF_VALIDATOR_NAME, lexeme)
            logging.debug(message)

    return ValidatorResult([definition_under_test], findings)


def _look_for_dupes(key, visited, pool):
    """Return duplicate name if found, otherwise None."""

    # key is the name we're evaluating
    # visited is the history of names we've alredy evaluated
    # pool is the dict of name to list of sub-items

    # work from a given key and use the pool to walk a depth-first-search through the pool
    #   to evaluate the "parent" through all the "children" recursively

    if key in visited:
        return key

    history = visited.copy()
    history.append(key)
    for value in pool[key]:
        return _look_for_dupes(value, history, pool)

    return None


def _get_site_tree(language_context):

    # Unit tests show that errors can occur across multiple invocations, so clear the tree to avoid data corruption between runs.
    # monitor this for potential performance slow-downs
    site_tree.clear()

    # creates a dict keyed by the site name with a value containing the list of sub-sites (or empty list)
    site_roots = language_context.get_definitions_by_root_key("site")
    for site in site_roots:
        if "sub-sites" in site.structure["site"].keys():
            subs = []
            for sub in site.structure["site"]["sub-sites"]:
                subs.append(sub["site-ref"])
            site_tree[site.name] = subs

        else:
            site_tree[site.name] = []


def _get_assembly_tree(language_context):

    # Unit tests show that errors can occur across multiple invocations, so clear the tree to avoid data corruption between runs.
    # monitor this for potential performance slow-downs
    assembly_tree.clear()

    # creates a dict keyed by assembly name with a value listing sub-assemblies (or empty list)
    assembly_roots = language_context.get_definitions_by_root_key("assembly")
    for assembly in assembly_roots:
        if "sub-assemblies" in assembly.structure["assembly"].keys():
            subs = []
            for sub in assembly.structure["assembly"]["sub-assemblies"]:
                subs.append(sub["assembly-ref"])
            assembly_tree[assembly.name] = subs

        else:
            assembly_tree[assembly.name] = []
