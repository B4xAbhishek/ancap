import { describe, it, expect } from "vitest";
import { parseWorkflowCsv, quoteWorkflowPlan } from "../workflowOps";

describe("workflow operations inputs", () => {
  it("parses quoted commas, newline cells, BOM and escaped quotes", () => {
    expect(parseWorkflowCsv('\uFEFFproject_name,description\r\nTeam,"line 1\nline 2, ""quoted"""\r\n')).toEqual([{ project_name: "Team", description: 'line 1\nline 2, "quoted"' }]);
  });
  it("rejects invalid headers, row sizes, malformed quoting and excess rows", () => {
    for (const data of ['name,name\na,b', '__proto__\nbad', 'name,description\none', 'name\n"unclosed', 'name\n' + Array(21).fill('x').join('\n')]) expect(() => parseWorkflowCsv(data)).toThrow();
  });
  it("calculates exact multi-step batch prices without assumed exchange rates", () => {
    expect(quoteWorkflowPlan(["588307.86", "1117784.92"], 3)).toBe("5118278.34");
    expect(quoteWorkflowPlan(["0.1", "0.2"], 2)).toBe("0.6");
    expect(quoteWorkflowPlan(["-1"])).toBeNull();
    expect(quoteWorkflowPlan(["1"], 21)).toBeNull();
  });
});
