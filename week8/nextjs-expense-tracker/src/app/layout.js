import "./globals.css";

export const metadata = {
  title: "가계부",
  description: "개인 가계부 앱",
};

export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
