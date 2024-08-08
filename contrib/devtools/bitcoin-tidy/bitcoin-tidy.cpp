// Copyright (c) 2023 Pingvincoin Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include "logprintf.h"
#include "nontrivial-threadlocal.h"

#include <clang-tidy/ClangTidyModule.h>
#include <clang-tidy/ClangTidyModuleRegistry.h>

class PingvincoinModule final : public clang::tidy::ClangTidyModule
{
public:
    void addCheckFactories(clang::tidy::ClangTidyCheckFactories& CheckFactories) override
    {
        CheckFactories.registerCheck<pingvincoin::LogPrintfCheck>("pingvincoin-unterminated-logprintf");
        CheckFactories.registerCheck<pingvincoin::NonTrivialThreadLocal>("pingvincoin-nontrivial-threadlocal");
    }
};

static clang::tidy::ClangTidyModuleRegistry::Add<PingvincoinModule>
    X("pingvincoin-module", "Adds pingvincoin checks.");

volatile int PingvincoinModuleAnchorSource = 0;
