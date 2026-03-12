#!/usr/bin/env node

const { program } = require('commander');
const inquirerModule = require('inquirer');
const fs = require('fs');
const path = require('path');

const inquirer = inquirerModule.default || inquirerModule;

function listCategories(categoriesRoot) {
  if (!fs.existsSync(categoriesRoot)) {
    return [];
  }

  return fs
    .readdirSync(categoriesRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

function getStarterFiles(language) {
  if (language === 'Python') {
    return {
      sourceFile: 'src/main.py',
      testFile: 'tests/test_main.py',
      sourceContent: 'def main():\n    return "placeholder"\n\n\nif __name__ == "__main__":\n    print(main())\n',
      testContent: 'from src.main import main\n\n\ndef test_main_returns_string():\n    assert isinstance(main(), str)\n',
      codeFence: 'python',
    };
  }

  if (language === 'Go') {
    return {
      sourceFile: 'src/main.go',
      testFile: 'tests/main_test.go',
      sourceContent: 'package main\n\nfunc main() {}\n',
      testContent: 'package main\n\nimport "testing"\n\nfunc TestPlaceholder(t *testing.T) {}\n',
      codeFence: 'go',
    };
  }

  if (language === 'Rust') {
    return {
      sourceFile: 'src/lib.rs',
      testFile: 'tests/lib_test.rs',
      sourceContent: 'pub fn placeholder() -> bool {\n    true\n}\n',
      testContent: '#[test]\nfn placeholder_test() {\n    assert!(true);\n}\n',
      codeFence: 'rust',
    };
  }

  return {
    sourceFile: 'src/index.js',
    testFile: 'tests/index.test.js',
    sourceContent: 'function main() {\n  return "placeholder";\n}\n\nmodule.exports = main;\n',
    testContent: 'const main = require("../src/index");\n\ntest("main returns a string", () => {\n  expect(typeof main()).toBe("string");\n});\n',
    codeFence: 'javascript',
  };
}

program
  .name('create-utility4iran')
  .description('Generate a utilities4iran module')
  .argument('[category]')
  .argument('[name]')
  .argument('[description]')
  .argument('[language]')
  .action(async (categoryArg, nameArg, descriptionArg, languageArg) => {
    const categoriesRoot = path.join(process.cwd(), 'categories');
    const existingCategories = listCategories(categoriesRoot);
    const NEW_CATEGORY = 'Create new category';

    const usingArgs = [categoryArg, nameArg, descriptionArg, languageArg].some(Boolean);

    let answers;

    if (usingArgs) {
      const supportedLanguages = ['JavaScript', 'Python', 'Go', 'Rust'];

      if (!categoryArg || !/^[a-z0-9-]+$/.test(categoryArg)) {
        throw new Error('Category must use lowercase, numbers, hyphens only');
      }

      if (!nameArg || !/^[a-z0-9-]+$/.test(nameArg)) {
        throw new Error('Module name must use lowercase, numbers, hyphens only');
      }

      if (!descriptionArg || descriptionArg.length <= 10) {
        throw new Error('Description must be at least 11 characters');
      }

      const language = languageArg || 'JavaScript';
      if (!supportedLanguages.includes(language)) {
        throw new Error(`Language must be one of: ${supportedLanguages.join(', ')}`);
      }

      answers = {
        categoryChoice: categoryArg,
        name: nameArg,
        description: descriptionArg,
        language,
      };
    } else {

      answers = await inquirer.prompt([
      {
        type: existingCategories.length > 0 ? 'list' : 'input',
        name: 'categoryChoice',
        message: 'Category:',
        choices: existingCategories.length > 0 ? [...existingCategories, NEW_CATEGORY] : undefined,
        validate: (input) => {
          if (existingCategories.length === 0) {
            return /^[a-z0-9-]+$/.test(input) || 'Use lowercase, numbers, hyphens only';
          }
          return true;
        },
      },
      {
        type: 'input',
        name: 'newCategory',
        message: 'New category name:',
        when: (answersSoFar) =>
          existingCategories.length === 0 || answersSoFar.categoryChoice === NEW_CATEGORY,
        validate: (input) => /^[a-z0-9-]+$/.test(input) || 'Use lowercase, numbers, hyphens only',
      },
      {
        type: 'input',
        name: 'name',
        message: 'Module name:',
        validate: i => /^[a-z0-9-]+$/.test(i) || 'Use lowercase, numbers, hyphens only'
      },
      {
        type: 'input',
        name: 'description',
        message: 'Description:',
        validate: i => i.length > 10 || 'At least 10 characters'
      },
      {
        type: 'list',
        name: 'language',
        message: 'Language:',
        choices: ['JavaScript', 'Python', 'Go', 'Rust']
      }
      ]);
    }

    const category = answers.newCategory || answers.categoryChoice;
    const starter = getStarterFiles(answers.language);

    const modulePath = path.join(process.cwd(), 'categories', category, answers.name);

    fs.mkdirSync(path.join(modulePath, 'src'), { recursive: true });
    fs.mkdirSync(path.join(modulePath, 'tests'), { recursive: true });

    const readme = `# ${answers.name}

${answers.description}

## Installation

\`\`\`bash
cd categories/${category}/${answers.name}
\`\`\`

## Usage

\`\`\`${starter.codeFence}
\`\`\`

## Testing

\`\`\`bash
\`\`\`

## Security

See SECURITY.md for security considerations.
`;

    const security = `# Security Policy

## Threat Model

Document what this module protects against and its limitations.

## Known Risks


## Reporting

Do not open public issues for security vulnerabilities.
`;

    fs.writeFileSync(path.join(modulePath, 'README.md'), readme);
    fs.writeFileSync(path.join(modulePath, 'SECURITY.md'), security);
  fs.writeFileSync(path.join(modulePath, starter.sourceFile), starter.sourceContent);
  fs.writeFileSync(path.join(modulePath, starter.testFile), starter.testContent);

  console.log(`✅ Created categories/${category}/${answers.name}`);
    console.log('\nNext steps:');
  console.log(`  cd categories/${category}/${answers.name}`);
    console.log('  # Implement your utility');
    console.log('  # Write tests');
    console.log('  # Submit PR');
  });

program.parse();
