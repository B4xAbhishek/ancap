import { walletUxCopy } from "../../locales/walletUx";
import { describe, expect, it } from "vitest";
import {
  acpUnits,
  maximumSend,
  parseBulkTransfers,
  transferCheck,
} from "../walletTransfer";
const address = "acp1" + "q".repeat(38);
describe("native ACP send boundaries", () => {
  it("reserves the fee exactly, including one-atom balances", () => {
    expect(maximumSend("1.000000000000000000", "0.00000100")).toBe("0.999999");
    expect(transferCheck(address, "1", "0.00000100", "1").error).toBe(
      "balance",
    );
    expect(transferCheck(address, "0.999999", "0.00000100", "1")).toEqual({
      error: null,
      total: "1",
    });
    expect(maximumSend("0.00000001", "0.00000100")).toBe("");
  });
  it("blocks unknown balances, invalid network addresses and hidden precision", () => {
    expect(transferCheck(address, "1", "0.00000100", null).error).toBe(
      "unavailable",
    );
    expect(transferCheck("0x1234", "1", "0.00000100", "5").error).toBe(
      "address",
    );
    for (const value of ["1e3", "-1", "NaN", "1.000000001", "1,5"])
      expect(acpUnits(value)).toBeNull();
  });
  it("validates every bulk row and cumulative fees before any send", () => {
    expect(() => parseBulkTransfers(`${address} 1\nwrong 2`, "10")).toThrow();
    expect(() =>
      parseBulkTransfers(`${address} 1\n${address} 2`, "10"),
    ).toThrow();
    expect(() =>
      parseBulkTransfers(`${address} 1\n${address.replace(/q$/, "p")} 1`, "2"),
    ).toThrow("balance");
    expect(parseBulkTransfers(`${address} 1`, "2").total).toBe("1.000001");
  });
});

it("keeps wallet labels complete across five languages", () => {
  const expected = Object.keys(walletUxCopy.en).sort();
  for (const copy of Object.values(walletUxCopy))
    expect(Object.keys(copy).sort()).toEqual(expected);
});
