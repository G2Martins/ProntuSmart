import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GestaoUsuarios } from './gestao-usuarios';

describe('GestaoUsuarios', () => {
    let component: GestaoUsuarios;
    let fixture: ComponentFixture<GestaoUsuarios>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [GestaoUsuarios],
        }).compileComponents();

        fixture = TestBed.createComponent(GestaoUsuarios);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
