import { redirect } from "next/navigation";

export default function ExnessReferral() {
  const exnessLink = process.env.NEXT_PUBLIC_EXNESS_LINK || "https://www.exness.com";
  redirect(exnessLink);
}
