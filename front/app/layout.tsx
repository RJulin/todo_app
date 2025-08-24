import './globals.css'

export const metadata = {
  title: 'AI boosted Todo Calendar App',
  description: 'A simple todo app with calendar integration',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
