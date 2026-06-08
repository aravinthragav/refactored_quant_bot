import { redirect } from "next/navigation";

export default function ExnessReferral() {
  const exnessLink = process.env.NEXT_PUBLIC_EXNESS_LINK || "https://one.exnessonelink.com/a/thvdkhvd";
  redirect(exnessLink);
}
