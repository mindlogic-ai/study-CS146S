import './globals.css';

export const metadata = {
  title: 'Notes & Action Items Manager',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
