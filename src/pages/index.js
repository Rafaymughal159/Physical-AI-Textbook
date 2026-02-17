import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './index.module.css'; // For homepage-specific styling

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={styles.heroBanner}>
      <div className="container">
        <div className={styles.heroContent}>
          {/* Left section: Book name and description */}
          <div className={styles.leftContent}>
            <h1 className="hero__title">{siteConfig.title}</h1>
            <p className="hero__subtitle">
              A comprehensive guide to the intersection of AI and the physical world.
              Explore robotics, embodied AI, and real-world applications.
            </p>
          </div>
          {/* Right section: Book logo */}
          <div className={styles.rightContent}>
            <img src="/img/logo.svg" alt="Book Logo" className={styles.homepageLogo} />
          </div>
        </div>
        {/* Button section */}
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Start Reading
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Homepage | ${siteConfig.title}`}
      description="The official homepage for the Physical AI Textbook.">
      <HomepageHeader />
      <main>
      </main>
    </Layout>
  );
}