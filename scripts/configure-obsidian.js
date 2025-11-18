#!/usr/bin/env node

import { ObsidianService } from '../src/services/obsidian.js';
import fs from 'fs';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Helper function to expand tilde
const expandTilde = (filePath) => {
    if (filePath.startsWith('~/')) {
        return path.join(os.homedir(), filePath.slice(2));
    }
    return filePath;
};

console.log('🔧 Obsidian Vault Configuration Helper');
console.log('=====================================\n');

// Common vault locations to check
const commonPaths = [
    // Default iCloud Obsidian vault (actual location)
    expandTilde('~/Library/Mobile Documents/iCloud~md~obsidian/Documents/PersonalAi'),
    // Other common locations
    expandTilde('~/Documents/PersonalAI'),
    expandTilde('~/Documents/ObsidianVault'),
    expandTilde('~/Documents/Obsidian'),
    expandTilde('~/Library/Mobile Documents/iCloud~md~obsidian/Documents'),
    expandTilde('~/Desktop/PersonalAI')
];

console.log('🔍 Checking common vault locations...\n');

let foundVaults = [];

for (const vaultPath of commonPaths) {
    try {
        if (fs.existsSync(vaultPath)) {
            console.log(`✅ Found potential vault: ${vaultPath}`);
            foundVaults.push(vaultPath);
        } else {
            console.log(`❌ Not found: ${vaultPath}`);
        }
    } catch (error) {
        console.log(`❌ Error checking: ${vaultPath}`);
    }
}

console.log('\n📋 Instructions:');
console.log('================');

if (foundVaults.length > 0) {
    console.log('Found potential Obsidian vaults. To use one:');
    foundVaults.forEach((vault, index) => {
        console.log(`${index + 1}. ${vault}`);
    });
} else {
    console.log('No vaults found in common locations.');
}

console.log('\n🛠️ To set up your vault:');
console.log('1. Open Obsidian and create a new vault');
console.log('2. Note the path where you created it');
console.log('3. Edit .env file and set OBSIDIAN_VAULT_PATH to your vault path');
console.log('4. Run: npm run test-obsidian');
console.log('\nExample .env entry (iCloud synced):');
console.log('OBSIDIAN_VAULT_PATH=/Users/jackdev/Library/Mobile Documents/iCloud~md~obsidian/Documents/PersonalAi');
console.log('\nExample .env entry (local):');
console.log('OBSIDIAN_VAULT_PATH=/Users/jackdev/Documents/PersonalAI');

// Test if we can initialize with current .env setting
const envPath = path.join(__dirname, '../../.env');
if (fs.existsSync(envPath)) {
    console.log('\n🧪 Testing current .env configuration...');
    
    // Simple env parser for testing
    const envContent = fs.readFileSync(envPath, 'utf-8');
    const vaultPathMatch = envContent.match(/OBSIDIAN_VAULT_PATH=(.+)/);
    
    if (vaultPathMatch && vaultPathMatch[1] !== '/path/to/your/obsidian/vault') {
        const configuredPath = vaultPathMatch[1];
        console.log(`📁 Configured path: ${configuredPath}`);
        
        if (fs.existsSync(configuredPath)) {
            console.log('✅ Vault path exists! Testing integration...');
            
            const obsidian = new ObsidianService(configuredPath);
            try {
                await obsidian.initialize();
                console.log('🎉 Obsidian integration working perfectly!');
            } catch (error) {
                console.log(`❌ Integration error: ${error.message}`);
            }
        } else {
            console.log('❌ Configured vault path does not exist');
        }
    } else {
        console.log('⚠️ Please update OBSIDIAN_VAULT_PATH in .env file');
    }
}