import Navbar from '../components/Navbar'
import { useTheme } from '../hooks/useTheme'

const sections = [
  {
    title: 'Information We Collect',
    content: [
      {
        sub: 'Account data',
        text: 'When you sign in with Google, we receive your email address and an OAuth access token. We store the email as your account identifier and the token (encrypted) to read your Google Sheets on your behalf.',
      },
      {
        sub: 'Notion credentials',
        text: 'When you connect Notion, we receive and store an OAuth token that allows BridgeFlow to create and update pages in the database you select.',
      },
      {
        sub: 'Sync configuration',
        text: 'We store the spreadsheet ID, sheet name, Notion database ID, column mappings, and id-column you configure through the app.',
      },
      {
        sub: 'Sync history',
        text: 'Every sync run generates a job record that includes row counts, error messages, and timestamps. This is used to show you the audit log inside the app.',
      },
    ],
  },
  {
    title: 'How We Use Your Information',
    content: [
      {
        sub: 'Performing the sync',
        text: 'Your Google token is used exclusively to read rows from the spreadsheet you specify. Your Notion token is used exclusively to create or update pages in the database you specify. No other data is accessed.',
      },
      {
        sub: 'Authentication',
        text: 'Your email identifies your account. We use a secure, HTTP-only session cookie to keep you signed in. Nothing is stored in localStorage or exposed to JavaScript.',
      },
      {
        sub: 'No advertising, no selling',
        text: 'We do not sell, rent, or share your data with any third party for advertising or marketing purposes.',
      },
    ],
  },
  {
    title: 'Third-Party Services',
    content: [
      {
        sub: 'Google APIs',
        text: 'BridgeFlow uses the Google Sheets API (read-only) to fetch your spreadsheet data. Your use of Google services is subject to Google\'s Privacy Policy.',
      },
      {
        sub: 'Notion API',
        text: 'BridgeFlow uses the Notion API to write to your database. Your use of Notion is subject to Notion\'s Privacy Policy.',
      },
      {
        sub: 'Database hosting',
        text: 'Account data and sync history are stored in a PostgreSQL database hosted on Neon (neon.tech). Data is encrypted at rest and in transit.',
      },
    ],
  },
  {
    title: 'Data Retention',
    content: [
      {
        sub: 'While your account exists',
        text: 'We retain your data for as long as your account is active. Sync job history is kept indefinitely unless you delete your account.',
      },
      {
        sub: 'On account deletion',
        text: 'Deleting your account removes all associated data from our database, including your tokens, configuration, and sync history. Reach out to us to request deletion.',
      },
    ],
  },
  {
    title: 'Your Rights',
    content: [
      {
        sub: 'Disconnect integrations',
        text: 'You can disconnect Google or Notion at any time from the Settings page. Disconnecting revokes BridgeFlow\'s access to that service.',
      },
      {
        sub: 'Data portability',
        text: 'Your sync configuration and job history are available through the app UI. Contact us if you need a full export.',
      },
      {
        sub: 'Deletion',
        text: 'Email us at hanamshettysunil6@gmail.com to request full account deletion.',
      },
    ],
  },
  {
    title: 'Contact',
    content: [
      {
        sub: 'Questions?',
        text: 'If you have any questions about this Privacy Policy or how we handle your data, email us at hanamshettysunil6@gmail.com.',
      },
    ],
  },
]

export default function PrivacyPolicy() {
  const { isDark, toggle } = useTheme()
  const bgClass = isDark ? 'bg-mesh-dark text-slate-100' : 'bg-mesh-light text-slate-800'
  const orb = 'absolute rounded-full blur-3xl pointer-events-none'

  return (
    <div className={`min-h-screen ${bgClass} transition-colors duration-500`}>
      <div className="relative overflow-hidden">
        <div className={`${orb} w-[500px] h-[500px] top-[-80px] left-[-80px] ${isDark ? 'bg-violet-700/10' : 'bg-violet-400/15'}`} />
        <div className={`${orb} w-[300px] h-[300px] top-[30%] right-[-60px] ${isDark ? 'bg-indigo-600/10' : 'bg-indigo-400/10'}`} />

        <Navbar isDark={isDark} toggleTheme={toggle} />

        <div className="max-w-3xl mx-auto px-6 pt-32 pb-20">
          {/* Header */}
          <div className="mb-12">
            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold mb-4 border
              ${isDark ? 'bg-violet-500/10 border-violet-500/20 text-violet-300' : 'bg-violet-100 border-violet-200 text-violet-700'}`}>
              <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
              Legal
            </div>
            <h1 className={`text-4xl sm:text-5xl font-black tracking-tight mb-4 ${isDark ? 'text-white' : 'text-slate-900'}`}>
              Privacy <span className="text-gradient">Policy</span>
            </h1>
            <p className={`text-base leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
              Last updated: June 2025
            </p>
            <p className={`mt-4 text-base leading-relaxed ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>
              BridgeFlow ("we", "us", "our") is committed to protecting your privacy. This policy explains
              what information we collect when you use BridgeFlow, how we use it, and what rights you have
              over it.
            </p>
          </div>

          {/* Sections */}
          <div className="space-y-10">
            {sections.map((section, i) => (
              <div key={section.title}>
                <h2 className={`text-xl font-black mb-5 flex items-center gap-3 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                  <span className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-black
                    bg-gradient-to-br from-violet-600 to-indigo-600 text-white shrink-0`}>
                    {i + 1}
                  </span>
                  {section.title}
                </h2>
                <div className={`rounded-2xl border divide-y overflow-hidden
                  ${isDark ? 'border-white/[0.07] divide-white/[0.05] bg-white/[0.02]' : 'border-violet-100 divide-violet-50 bg-white/70'}`}>
                  {section.content.map((item) => (
                    <div key={item.sub} className="px-6 py-5">
                      <p className={`text-sm font-bold mb-1.5 ${isDark ? 'text-slate-200' : 'text-slate-800'}`}>
                        {item.sub}
                      </p>
                      <p className={`text-sm leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                        {item.text}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Back link */}
          <div className="mt-14 pt-8 border-t border-white/[0.06]">
            <a
              href="/"
              className={`inline-flex items-center gap-2 text-sm font-medium transition-colors
                ${isDark ? 'text-violet-400 hover:text-violet-300' : 'text-violet-600 hover:text-violet-700'}`}
            >
              <svg viewBox="0 0 20 20" className="w-4 h-4" fill="currentColor">
                <path fillRule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clipRule="evenodd"/>
              </svg>
              Back to BridgeFlow
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
