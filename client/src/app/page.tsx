import Link from "next/link";
import {
  Shield,
  Lock,
  FileText,
  ChevronRight,
  CheckCircle,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <header className="container mx-auto px-4 py-8 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <Shield className="w-8 h-8 text-blue-600" />
          <span className="text-2xl font-bold text-gray-800">Fidelius</span>
        </div>
        <nav>
          <ul className="flex space-x-6">
            <li>
              <Link
                href="#features"
                className="text-gray-900 hover:text-blue-600 transition-colors"
              >
                Features
              </Link>
            </li>
            <li>
              <Link
                href="#how-it-works"
                className="text-gray-900 hover:text-blue-600 transition-colors"
              >
                How It Works
              </Link>
            </li>
            <li>
              <Link
                href="#pricing"
                className="text-gray-900 hover:text-blue-600 transition-colors"
              >
                Pricing
              </Link>
            </li>
          </ul>
        </nav>
      </header>

      <main>
        <section className="container mx-auto px-4 py-20 text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Secure Your Sensitive Data with Fidelius
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
            Easily mask and obfuscate your files to protect confidential
            information. Keep your data safe without compromising its usability.
          </p>
          <Link
            href="/readFile"
            className="bg-blue-600 text-white px-8 py-4 rounded-full text-lg font-semibold hover:bg-blue-700 transition-colors inline-flex items-center"
          >
            Get Started
            <ChevronRight className="ml-2 w-5 h-5" />
          </Link>
        </section>

        <section id="features" className="bg-white py-20">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
              Key Features
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-blue-50 p-6 rounded-lg">
                <Lock className="w-12 h-12 text-blue-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2 text-gray-600">
                  Advanced Encryption
                </h3>
                <p className="text-gray-600">
                  Protect your files with state-of-the-art encryption
                  algorithms.
                </p>
              </div>
              <div className="bg-blue-50 p-6 rounded-lg">
                <FileText className="w-12 h-12 text-blue-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2 text-gray-600">
                  Multiple File Formats
                </h3>
                <p className="text-gray-600">
                  Support for various file types including documents,
                  spreadsheets, and more.
                </p>
              </div>
              <div className="bg-blue-50 p-6 rounded-lg">
                <Shield className="w-12 h-12 text-blue-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2 text-gray-600">
                  Customizable Masking
                </h3>
                <p className="text-gray-600">
                  Tailor the level of obfuscation to meet your specific needs.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="py-20">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
              How It Works
            </h2>
            <div className="max-w-3xl mx-auto">
              <ol className="relative border-l border-gray-200">
                <li className="mb-10 ml-6">
                  <span className="text-black absolute flex items-center justify-center w-8 h-8 bg-blue-100 rounded-full -left-4 ring-4 ring-white">
                    1
                  </span>
                  <h3 className="text-black font-semibold text-lg mb-1">
                    Upload Your File
                  </h3>
                  <p className="text-gray-600">
                    Securely upload the file you want to mask or obfuscate.
                  </p>
                </li>
                <li className="mb-10 ml-6">
                  <span className="text-black absolute flex items-center justify-center w-8 h-8 bg-blue-100 rounded-full -left-4 ring-4 ring-white">
                    2
                  </span>
                  <h3 className="text-black font-semibold text-lg mb-1">
                    Choose Masking Options
                  </h3>
                  <p className="text-gray-600">
                    Select the level of masking and specific areas to obfuscate.
                  </p>
                </li>
                <li className="mb-10 ml-6">
                  <span className="text-black absolute flex items-center justify-center w-8 h-8 bg-blue-100 rounded-full -left-4 ring-4 ring-white">
                    3
                  </span>
                  <h3 className="text-black font-semibold text-lg mb-1">
                    Process and Download
                  </h3>
                  <p className="text-gray-600">
                    Our system processes your file and provides a secure
                    download link.
                  </p>
                </li>
              </ol>
            </div>
          </div>
        </section>

        {/* <section id='pricing' className='bg-blue-50 py-20'>
          <div className='container mx-auto px-4'>
            <h2 className='text-3xl font-bold text-center text-gray-900 mb-12'>
              Simple, Transparent Pricing
            </h2>
            <div className='max-w-sm mx-auto bg-white rounded-lg shadow-lg overflow-hidden'>
              <div className='px-6 py-8'>
                <h3 className='text-black text-2xl font-semibold text-center mb-4'>
                  Pro Plan
                </h3>
                <div className='text-center mb-6'>
                  <span className='text-black text-4xl font-bold'>$19.99</span>
                  <span className='text-black'>/month</span>
                </div>
                <ul className='mb-6'>
                  <li className='flex items-center mb-2'>
                    <CheckCircle className='w-5 h-5 text-green-500 mr-2' />
                    <span className='text-black'>Unlimited file masking</span>
                  </li>
                  <li className='flex items-center mb-2'>
                    <CheckCircle className='w-5 h-5 text-green-500 mr-2' />
                    <span className='text-black'>
                      Advanced encryption options
                    </span>
                  </li>
                  <li className='flex items-center mb-2'>
                    <CheckCircle className='w-5 h-5 text-green-500 mr-2' />
                    <span className='text-black'>Priority support</span>
                  </li>
                </ul>
                <button className='w-full bg-blue-600 text-white px-4 py-2 rounded-full font-semibold hover:bg-blue-700 transition-colors'>
                  Get Started
                </button>
              </div>
            </div>
          </div>
        </section> */}
      </main>

      <footer className="bg-gray-800 text-white py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <div className="flex items-center space-x-2">
                <Shield className="w-6 h-6 text-blue-400" />
                <span className="text-xl font-bold">FileMask</span>
              </div>
              <p className="text-sm text-gray-400 mt-2">
                Secure your files with confidence
              </p>
            </div>
            <nav>
              <ul className="flex space-x-6">
                <li>
                  <Link
                    href="/privacy"
                    className="hover:text-blue-400 transition-colors"
                  >
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link
                    href="/terms"
                    className="hover:text-blue-400 transition-colors"
                  >
                    Terms of Service
                  </Link>
                </li>
                <li>
                  <Link
                    href="/contact"
                    className="hover:text-blue-400 transition-colors"
                  >
                    Contact Us
                  </Link>
                </li>
              </ul>
            </nav>
          </div>
          <div className="mt-8 text-center text-sm text-gray-400">
            © {new Date().getFullYear()} FileMask. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
