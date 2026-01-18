import { z } from "zod";
import type { TFunction } from "i18next";

// Constants matching backend constraints
export const FILTER_CONSTRAINTS = {
  MAX_RULE_GROUPS: 5,
  MAX_RULES_PER_GROUP: 10,
  MAX_VALUE_LENGTH: 200,
  ALLOWED_FIELDS: ["title"] as const,
  ALLOWED_OPERATORS: ["contains", "not_contains"] as const,
  ALLOWED_LOGIC: ["and", "or"] as const,
} as const;

// Schema factory - accepts translation function for localized messages
export const createFilterSchemas = (t: TFunction) => {
  const filterRuleSchema = z.object({
    field: z.enum(FILTER_CONSTRAINTS.ALLOWED_FIELDS),
    operator: z.enum(FILTER_CONSTRAINTS.ALLOWED_OPERATORS),
    value: z
      .string()
      .min(1, { message: t("filters.errors.valueEmpty") })
      .max(FILTER_CONSTRAINTS.MAX_VALUE_LENGTH, {
        message: t("filters.errors.valueTooLong", {
          maxLength: FILTER_CONSTRAINTS.MAX_VALUE_LENGTH,
        }),
      })
      .transform((v) => v.trim())
      .refine((v) => v.length > 0, {
        message: t("filters.errors.valueOnlyWhitespace"),
      }),
    caseSensitive: z.boolean().default(false),
  });

  const ruleGroupSchema = z.object({
    logic: z.enum(FILTER_CONSTRAINTS.ALLOWED_LOGIC).default("and"),
    logicWithNext: z.enum(FILTER_CONSTRAINTS.ALLOWED_LOGIC).optional(),
    rules: z
      .array(filterRuleSchema)
      .min(1, { message: t("filters.errors.groupMustHaveRules") })
      .max(FILTER_CONSTRAINTS.MAX_RULES_PER_GROUP, {
        message: t("filters.errors.tooManyRules", {
          maxRules: FILTER_CONSTRAINTS.MAX_RULES_PER_GROUP,
        }),
      }),
  });

  const filtersConfigSchema = z.object({
    ruleGroups: z
      .array(ruleGroupSchema)
      .min(1, { message: t("filters.errors.noGroups") })
      .max(FILTER_CONSTRAINTS.MAX_RULE_GROUPS, {
        message: t("filters.errors.tooManyGroups", {
          maxGroups: FILTER_CONSTRAINTS.MAX_RULE_GROUPS,
        }),
      }),
  });

  return {
    filterRuleSchema,
    ruleGroupSchema,
    filtersConfigSchema,
  };
};

// Base schemas for type inference (without translations)
const baseFilterRuleSchema = z.object({
  field: z.enum(FILTER_CONSTRAINTS.ALLOWED_FIELDS),
  operator: z.enum(FILTER_CONSTRAINTS.ALLOWED_OPERATORS),
  value: z.string().min(1).max(FILTER_CONSTRAINTS.MAX_VALUE_LENGTH),
  caseSensitive: z.boolean().default(false),
});

const baseRuleGroupSchema = z.object({
  logic: z.enum(FILTER_CONSTRAINTS.ALLOWED_LOGIC).default("and"),
  logicWithNext: z.enum(FILTER_CONSTRAINTS.ALLOWED_LOGIC).optional(),
  rules: z.array(baseFilterRuleSchema).min(1).max(FILTER_CONSTRAINTS.MAX_RULES_PER_GROUP),
});

const baseFiltersConfigSchema = z.object({
  ruleGroups: z.array(baseRuleGroupSchema).min(1).max(FILTER_CONSTRAINTS.MAX_RULE_GROUPS),
});

// Type inference from base schemas - much simpler!
export type FilterRule = z.infer<typeof baseFilterRuleSchema>;
export type RuleGroup = z.infer<typeof baseRuleGroupSchema>;
export type FiltersConfig = z.infer<typeof baseFiltersConfigSchema>;
