/**
 * Tests for credentials store
 */
import { renderHook, act } from "@testing-library/react";
import { useCredentialsStore } from "@/store/credentials";

describe("CredentialsStore", () => {
  beforeEach(() => {
    // Clear store before each test
    useCredentialsStore.getState().clearCredentials();
  });

  it("should initialize with no credentials", () => {
    const { result } = renderHook(() => useCredentialsStore());
    expect(result.current.hasCredentials()).toBe(false);
    expect(result.current.getCredentials()).toBe(null);
  });

  it("should set and get credentials", () => {
    const { result } = renderHook(() => useCredentialsStore());
    
    act(() => {
      result.current.setCredentials({
        deltaApiKey: "test_key",
        deltaApiSecret: "test_secret",
        deltaBaseUrl: "https://api.test.delta.exchange",
      });
    });

    expect(result.current.hasCredentials()).toBe(true);
    const credentials = result.current.getCredentials();
    expect(credentials?.deltaApiKey).toBe("test_key");
    expect(credentials?.deltaApiSecret).toBe("test_secret");
  });

  it("should clear credentials", () => {
    const { result } = renderHook(() => useCredentialsStore());
    
    act(() => {
      result.current.setCredentials({
        deltaApiKey: "test_key",
        deltaApiSecret: "test_secret",
      });
    });

    expect(result.current.hasCredentials()).toBe(true);

    act(() => {
      result.current.clearCredentials();
    });

    expect(result.current.hasCredentials()).toBe(false);
    expect(result.current.getCredentials()).toBe(null);
  });
});





