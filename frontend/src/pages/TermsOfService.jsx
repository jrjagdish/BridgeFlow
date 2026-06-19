import Navbar from '../components/Navbar'
import { useTheme } from '../hooks/useTheme'

const sections = [
  {
    title: 'Acceptance of Terms',
    items: [
      'By accessing or using BridgeFlow you agree to be bound by these Terms of Service. If you do not agree, do not use the service.',
      'We may update these terms at any time. Continued use of BridgeFlow after changes are posted constitutes acceptance of the revised terms.',
    ],
  },
  {
    title: 'Description of Service',
    items: [
      'BridgeFlow is a data-sync tool that reads rows from a Google Sheets spreadsheet and writes them into a Notion database on your behalf.',
      'BridgeFlow is provided as open-source software (MIT licence). You may self-host it free of charge. A hosted version ("BridgeFlow Pro") is planned but not yet available.',
      'We reserve the right to modify, suspend, or discontinue the hosted service at any time without notice.',
    ],
  },
  {
    title: 'Your Account and Responsibilities',
    items: [
      'You are responsible for maintaining the security of your Google account and Notion workspace. BridgeFlow only stores the OAuth tokens you explicitly grant us.',
      'You must not use BridgeFlow to sync data you do not own or do not have permission to access.',
      'You are responsible for the content of the spreadsheets and Notion databases you connect to BridgeFlow.',
      'One account per person. You may not share your session or credentials with others.',
    ],
  },
  {
    title: 'Acceptable Use',
    items: [
      'You may not use BridgeFlow for any unlawful purpose or in any way that violates applicable laws or regulations.',
      'You may not attempt to reverse-engineer, overload, or interfere with the BridgeFlow service infrastructure.',
      'Automated or scripted abuse of the API endpoints (beyond normal application use) is prohibited.',
      'We reserve the right to suspend or terminate access for any violation of these terms.',
    ],
  },
  {
    title: 'Third-Party Services',
    items: [
      'BridgeFlow integrates with Google Sheets and Notion via their respective public APIs. Your use of those services is governed by Google\'s and Notion\'s own terms of service.',
      'We are not responsible for the availability, accuracy, or behaviour of third-party APIs. Downtime or changes to Google or Notion APIs may affect BridgeFlow\'s functionality.',
    ],
  },
  {
    title: 'Intellectual Property',
    items: [
      'BridgeFlow\'s source code is released under the MIT licence. You are free to use, copy, modify, merge, publish, and distribute it subject to the terms of that licence.',
      'The BridgeFlow name and logo are trademarks of the project maintainers. You may not use them to imply endorsement of a derivative product without permission.',
    ],
  },
  {
    title: 'Disclaimer of Warranties',
    items: [
      'BridgeFlow is provided "as is" and "as available" without warranties of any kind, express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, or non-infringement.',
      'We do not warrant that the service will be uninterrupted, error-free, or that data will never be lost. Always keep your own backups of important data.',
    ],
  },
  {
    title: 'Limitation of Liability',
    items: [
      'To the fullest extent permitted by law, BridgeFlow and its contributors shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising out of your use of the service.',
      'Our total liability to you for any claim arising out of or relating to these terms or the service shall not exceed the amount you paid us in the twelve months preceding the claim (or $0 if you used the free tier).',
    ],
  },
  {
    title: 'Contact',
    items: [
      'For questions about these Terms of Service, email us at hanamshettysunil6@gmail.com.',
    ],
  },
]

export default function TermsOfService() {
  const { isDark, toggle } = useTheme()
  const bgClass = isDark ? 'bg-mesh-dark text-slate-100' : 'bg-mesh-light text-slate-800'
  const orb = 'absolute rounded-full blur-3xl pointer-events-none'

  return (
    <div className={`min-h-screen ${bgClass} transition-colors duration-500`}>
      <div className="relative overflow-hidden">
        <div className={`${orb} w-[500px] h-[500px] top-[-80px] right-[-80px] ${isDark ? 'bg-indigo-700/10' : 'bg-indigo-400/15'}`} />
        <div className={`${orb} w-[300px] h-[300px] top-[40%] left-[-60px] ${isDark ? 'bg-violet-600/10' : 'bg-violet-400/10'}`} />

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
              Terms of <span className="text-gradient">Service</span>
            </h1>
            <p className={`text-base leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
              Last updated: June 2025
            </p>
            <p className={`mt-4 text-base leading-relaxed ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>
              Please read these Terms of Service carefully before using BridgeFlow. By using the service you
              agree to be bound by these terms.
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
                  {section.items.map((text, j) => (
                    <div key={j} className="px-6 py-4 flex gap-3">
                      <span className={`mt-0.5 w-1.5 h-1.5 rounded-full shrink-0 ${isDark ? 'bg-violet-500' : 'bg-violet-400'}`} />
                      <p className={`text-sm leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                        {text}
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
