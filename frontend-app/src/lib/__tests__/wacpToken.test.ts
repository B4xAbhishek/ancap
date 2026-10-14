import { describe, it, expect } from "vitest";
import { buildWacpWatchAssetParams, getWacpLogoUrl, WACP_BSC_CONTRACT } from "@/lib/wacpToken";

describe("wacpToken", () => {
  it("builds EIP-747 watchAsset params with logo URL", () => {
    const params = buildWacpWatchAssetParams(
      WACP_BSC_CONTRACT,
      "https://ancap.cloud/wacp-logo.png",
    );
    expect(params).toEqual({
      type: "ERC20",
      options: {
        address: WACP_BSC_CONTRACT,
        symbol: "wACP",
        decimals: 18,
        image: "https://ancap.cloud/wacp-logo.png",
      },
    });
  });

  it("uses site origin for token image when provided", () => {
    expect(getWacpLogoUrl("http://localhost:3000")).toBe(
      "http://localhost:3000/wacp-logo.png",
    );
  });
});
