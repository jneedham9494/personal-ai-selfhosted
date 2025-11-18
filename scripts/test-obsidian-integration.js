#!/usr/bin/env node

import dotenv from 'dotenv';
import { ObsidianService } from '../src/services/obsidian.js';

// Load environment variables
dotenv.config();

console.log('🧪 Testing Obsidian Integration');
console.log('===============================\n');

const vaultPath = process.env.OBSIDIAN_VAULT_PATH;
console.log(`📁 Vault path: ${vaultPath}`);

if (!vaultPath || vaultPath === '/path/to/your/obsidian/vault') {
    console.error('❌ Please set OBSIDIAN_VAULT_PATH in .env file');
    process.exit(1);
}

try {
    console.log('🔄 Initializing Obsidian service...');
    const obsidian = new ObsidianService(vaultPath);
    
    await obsidian.initialize();
    
    console.log('\n🎉 Obsidian integration working!');
    console.log('✅ Vault accessible');
    console.log('✅ Folders created');
    console.log('✅ Templates ready');
    
    // Test saving a conversation
    console.log('\n🧪 Testing conversation save...');
    const testConversation = {
        platform: 'test',
        messages: [
            { role: 'user', content: 'Hello, this is a test message' },
            { role: 'assistant', content: 'Hello! This is a test response from the AI assistant.' }
        ],
        topic: 'Integration Test',
        metadata: { test: true }
    };
    
    const savedPath = await obsidian.saveConversation(testConversation);
    console.log(`✅ Test conversation saved: ${savedPath}`);
    
    // Test search
    console.log('\n🔍 Testing search...');
    const searchResults = await obsidian.searchNotes('test');
    console.log(`✅ Found ${searchResults.length} matching notes`);
    
    // Test today's note
    console.log('\n📅 Testing daily note...');
    const todaysNote = await obsidian.getTodaysNote();
    console.log(`✅ Today's note: ${todaysNote.path}`);
    
    await obsidian.close();
    
    console.log('\n🎉 All tests passed! Obsidian integration is ready.');
    
} catch (error) {
    console.error(`❌ Error: ${error.message}`);
    
    if (error.message.includes('not found')) {
        console.log('\n💡 Troubleshooting:');
        console.log('1. Check that Obsidian vault "personalai" exists in iCloud');
        console.log('2. Verify the exact vault name (case-sensitive)');
        console.log('3. Make sure iCloud sync is working');
        console.log('4. You might need to grant permission to access iCloud files');
    }
    
    process.exit(1);
}