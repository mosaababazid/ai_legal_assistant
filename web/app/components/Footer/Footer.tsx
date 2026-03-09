"use client";

import "./Footer.css";

const DEVELOPER = {
  name: "Mosaab Abazid",
  website: "https://mosaababazid.com/",
  email: "contact@mosaababazid.com",
  github: "https://github.com/mosaababazid",
  linkedin: "https://www.linkedin.com/in/mosaababazid",
};

export type FooterProps = {
  developedLabel: string;
  developedTextFull?: string;
  websiteLabel: string;
  emailLabel: string;
  githubLabel: string;
  linkedinLabel: string;
  isRtl: boolean;
};

export function Footer({
  developedLabel,
  developedTextFull,
  websiteLabel,
  emailLabel,
  githubLabel,
  linkedinLabel,
  isRtl,
}: FooterProps) {
  const developedLine = developedTextFull ?? (
    <>
      {developedLabel}{" "}
      <strong>{DEVELOPER.name}</strong>
    </>
  );

  return (
    <footer className={`footer ${isRtl ? "font-arabic" : ""}`} role="contentinfo">
      <div className="footer__inner">
        <div className={`footer__block ${isRtl ? "footer__block--rtl" : ""}`}>
          <p className="footer__line">
            {developedLine}
          </p>
          <div className="footer__links">
            <a
              href={DEVELOPER.website}
              target="_blank"
              rel="noopener noreferrer"
              className="footer__link"
            >
              {websiteLabel}: mosaababazid.com
            </a>
            <a href={`mailto:${DEVELOPER.email}`} className="footer__link">
              {emailLabel}: {DEVELOPER.email}
            </a>
            <a
              href={DEVELOPER.github}
              target="_blank"
              rel="noopener noreferrer"
              className="footer__link"
            >
              {githubLabel}
            </a>
            <a
              href={DEVELOPER.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              className="footer__link"
            >
              {linkedinLabel}
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}